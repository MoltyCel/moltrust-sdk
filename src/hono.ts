// Hono adapter
import { evaluate } from '@moltrust/aae';
import type { VerifyOptions } from './types';
import { fetchTrustScore, fetchCredentialAAE } from './client';
import { extractFromHeaders } from './extract';

export function honoVerify(options: VerifyOptions = {}) {
  const {
    minScore = 0,
    requireAAE = false,
    evaluateAction,
    evaluateAmount,
    evaluateJurisdiction,
    apiBase = 'https://api.moltrust.ch',
  } = options;

  return async function(c: any, next: any): Promise<any> {
    const headers = Object.fromEntries(c.req.raw.headers.entries());
    const { did, credentialId } = extractFromHeaders(headers);

    if (!did) return next();

    try {
      const scoreData = await fetchTrustScore(did, apiBase);

      if (minScore > 0 && scoreData.trust_score < minScore) {
        return c.json({
          error: 'agent_trust_score_insufficient',
          trust_score: scoreData.trust_score,
          required: minScore
        }, 403);
      }

      let aae = credentialId ? await fetchCredentialAAE(credentialId, apiBase) : undefined;

      if (requireAAE && !aae) {
        return c.json({ error: 'agent_aae_required' }, 403);
      }

      if (aae && evaluateAction) {
        const evaluation = evaluate(aae, {
          action: evaluateAction,
          amount: evaluateAmount,
          jurisdiction: evaluateJurisdiction,
        });
        if (!evaluation.allowed) {
          return c.json({ error: 'agent_action_not_permitted', reason: evaluation.reason }, 403);
        }
      }

      c.set('agentVerification', {
        did,
        trustScore: scoreData.trust_score,
        grade: scoreData.grade,
        aae,
        credentialId,
        verified: true,
      });

      return next();
    } catch {
      if (minScore > 0) return c.json({ error: 'agent_verification_unavailable' }, 503);
      return next();
    }
  };
}
