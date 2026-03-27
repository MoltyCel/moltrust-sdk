import { fetchTrustScore } from './client';
import { verify as expressMiddleware } from './middleware';
import { honoVerify } from './hono';
import type {
  VerificationResult,
  StandaloneVerifyOptions,
  VerifyOptions,
  RegisterOptions,
} from './types';

const DEFAULT_API = 'https://api.moltrust.ch';

/**
 * MolTrust Agent Verification — standalone + middleware.
 *
 * Standalone:
 *   const result = await AgentTrust.verify('did:moltrust:abc123');
 *
 * Express middleware:
 *   app.use('/api', AgentTrust.middleware({ minScore: 70 }));
 *
 * Hono middleware:
 *   app.use('/api', AgentTrust.honoMiddleware({ minScore: 70 }));
 */
export class AgentTrust {
  /**
   * Verify an agent's trust score. Returns a result object — never throws.
   *
   * @example
   * const result = await AgentTrust.verify('did:moltrust:abc123');
   * if (!result.verified) throw new Error(result.reason);
   *
   * @example
   * const result = await AgentTrust.verify('did:moltrust:abc123', {
   *   minScore: 70,
   *   blockFlags: ['young_endorser_cluster'],
   * });
   */
  static async verify(
    did: string,
    options: StandaloneVerifyOptions = {},
  ): Promise<VerificationResult> {
    const {
      minScore = 0,
      blockFlags = [],
      timeout = 5000,
      apiBase = DEFAULT_API,
    } = options;

    try {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), timeout);

      let data;
      try {
        const res = await fetch(
          `${apiBase}/skill/trust-score/${encodeURIComponent(did)}`,
          { signal: controller.signal },
        );
        if (!res.ok) throw new Error(`API ${res.status}`);
        data = await res.json() as any;
      } finally {
        clearTimeout(timer);
      }

      const score: number = data.trust_score ?? 0;
      const grade: string = data.grade ?? 'F';
      const flags: string[] = data.flags ?? [];

      // Withheld score (< 3 endorsers)
      if (data.withheld) {
        return {
          verified: false,
          did,
          trustScore: 0,
          grade: 'N/A',
          flags: [],
          reason: 'Trust score withheld — insufficient endorsements',
          checkedAt: new Date().toISOString(),
        };
      }

      // Check minScore
      if (minScore > 0 && score < minScore) {
        return {
          verified: false,
          did,
          trustScore: score,
          grade,
          flags,
          reason: `Trust score ${score} below minimum ${minScore}`,
          checkedAt: new Date().toISOString(),
        };
      }

      // Check blocked flags
      if (blockFlags.length > 0) {
        const blocked = flags.filter((f) => blockFlags.includes(f));
        if (blocked.length > 0) {
          return {
            verified: false,
            did,
            trustScore: score,
            grade,
            flags,
            reason: `Blocked flags present: ${blocked.join(', ')}`,
            checkedAt: new Date().toISOString(),
          };
        }
      }

      return {
        verified: true,
        did,
        trustScore: score,
        grade,
        flags,
        checkedAt: new Date().toISOString(),
      };
    } catch (err) {
      return {
        verified: false,
        did,
        trustScore: 0,
        grade: 'F',
        flags: [],
        reason: `Verification failed: ${err instanceof Error ? err.message : 'unknown error'}`,
        checkedAt: new Date().toISOString(),
      };
    }
  }

  /**
   * Express middleware — reads DID from X-Agent-DID header.
   * Returns 403 if verification fails.
   *
   * @example
   * app.use('/api/action', AgentTrust.middleware({ minScore: 70 }));
   */
  static middleware(options?: VerifyOptions) {
    return expressMiddleware(options);
  }

  /**
   * Hono middleware — reads DID from X-Agent-DID header.
   * Returns 403 if verification fails.
   *
   * @example
   * app.use('/api/action', AgentTrust.honoMiddleware({ minScore: 70 }));
   */
  static honoMiddleware(options?: VerifyOptions) {
    return honoVerify(options);
  }

  /**
   * Register a new agent at MolTrust.
   *
   * @example
   * const agent = await AgentTrust.register({
   *   displayName: 'My Trading Agent',
   *   apiKey: process.env.MOLTRUST_API_KEY!,
   * });
   */
  static async register(params: RegisterOptions) {
    const res = await fetch(`${DEFAULT_API}/identity/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': params.apiKey,
      },
      body: JSON.stringify({
        display_name: params.displayName,
        platform: params.platform ?? 'custom',
        public_key: params.publicKey,
      }),
    });
    if (!res.ok) throw new Error(`Registration failed: ${res.status}`);
    return res.json();
  }
}
