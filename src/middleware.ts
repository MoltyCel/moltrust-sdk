import type { Request, Response, NextFunction } from 'express';
import { evaluate } from '@moltrust/aae';
import type { VerifyOptions, AgentVerification } from './types';
import { fetchTrustScore, fetchCredentialAAE } from './client';
import { extractFromHeaders } from './extract';

export function verify(options: VerifyOptions = {}) {
  const {
    minScore = 0,
    blockFlags = [],
    requireAAE = false,
    evaluateAction,
    evaluateAmount,
    evaluateJurisdiction,
    apiBase = 'https://api.moltrust.ch',
  } = options;

  return async function agentTrustMiddleware(
    req: Request,
    res: Response,
    next: NextFunction
  ): Promise<void> {
    // 1. Extract agent DID from request
    const { did, credentialId } = extractFromHeaders(req.headers as Record<string, string | undefined>);

    if (!did) {
      // No DID present — pass through (non-agent request)
      return next();
    }

    try {
      // 2. Fetch trust score
      const scoreData = await fetchTrustScore(did, apiBase);

      const flags = scoreData.flags ?? [];

      // 3. Check minimum score
      if (minScore > 0 && scoreData.trust_score < minScore) {
        res.status(403).json({
          error: 'agent_trust_score_insufficient',
          did,
          trust_score: scoreData.trust_score,
          required: minScore
        });
        return;
      }

      // 3b. Check blocked flags
      if (blockFlags.length > 0) {
        const blocked = flags.filter((f: string) => blockFlags.includes(f));
        if (blocked.length > 0) {
          res.status(403).json({
            error: 'agent_blocked_flags',
            did,
            flags: blocked,
          });
          return;
        }
      }

      // 4. Fetch AAE if credential provided
      let aae = undefined;
      let aaeEvaluation = undefined;

      if (credentialId) {
        aae = await fetchCredentialAAE(credentialId, apiBase);
      }

      if (requireAAE && !aae) {
        res.status(403).json({
          error: 'agent_aae_required',
          did,
          message: 'A valid Agent Authorization Envelope is required'
        });
        return;
      }

      // 5. Evaluate AAE if present and action specified
      if (aae && evaluateAction) {
        aaeEvaluation = evaluate(aae, {
          action: evaluateAction,
          amount: evaluateAmount,
          jurisdiction: evaluateJurisdiction,
        });

        if (!aaeEvaluation.allowed) {
          res.status(403).json({
            error: 'agent_action_not_permitted',
            did,
            reason: aaeEvaluation.reason,
          });
          return;
        }
      }

      // 6. Attach verification result to request
      const verification: AgentVerification = {
        did,
        trustScore: scoreData.trust_score,
        grade: scoreData.grade,
        flags,
        aae,
        aaeEvaluation,
        credentialId: credentialId ?? undefined,
        verified: true,
      };

      req.agentVerification = verification;
      next();

    } catch (err) {
      // API error — fail open (log but continue) or fail closed based on minScore
      if (minScore > 0) {
        res.status(503).json({
          error: 'agent_verification_unavailable',
          message: 'Could not verify agent trust score'
        });
        return;
      }
      next();
    }
  };
}
