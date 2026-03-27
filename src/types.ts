import type { AAE, EvaluationResult } from '@moltrust/aae';

export interface AgentVerification {
  did: string;
  trustScore: number;
  grade: string;
  flags: string[];
  aae?: AAE;
  aaeEvaluation?: EvaluationResult;
  credentialId?: string;
  verified: boolean;
}

/** Result from standalone AgentTrust.verify(did) */
export interface VerificationResult {
  verified: boolean;
  did: string;
  trustScore: number;
  grade: string;
  flags: string[];
  reason?: string;
  checkedAt: string;
}

/** Options for standalone AgentTrust.verify(did, options) */
export interface StandaloneVerifyOptions {
  minScore?: number;
  blockFlags?: string[];
  timeout?: number;
  apiBase?: string;
}

/** Options for middleware (Express/Hono) */
export interface VerifyOptions {
  minScore?: number;           // minimum trust score (0-100), default: 0
  blockFlags?: string[];       // flags that trigger 403
  requireAAE?: boolean;        // require AAE in credential, default: false
  evaluateAction?: string;     // URI of action to evaluate against AAE
  evaluateAmount?: number;     // transaction amount for threshold checks
  evaluateJurisdiction?: string; // ISO 3166-1 alpha-2
  onUnauthorized?: (reason: string) => void; // custom handler
  apiBase?: string;            // MolTrust API base URL, default: https://api.moltrust.ch
}

/** Options for AgentTrust.register() */
export interface RegisterOptions {
  displayName: string;
  platform?: string;
  publicKey?: string;
  apiKey: string;
}

// Express augmentation
declare global {
  namespace Express {
    interface Request {
      agentVerification?: AgentVerification;
    }
  }
}
