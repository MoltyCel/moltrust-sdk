import type { AAE, EvaluationResult } from '@moltrust/aae';

export interface AgentVerification {
  did: string;
  trustScore: number;
  grade: string;
  aae?: AAE;
  aaeEvaluation?: EvaluationResult;
  credentialId?: string;
  verified: boolean;
}

export interface VerifyOptions {
  minScore?: number;           // minimum trust score (0-100), default: 0
  requireAAE?: boolean;        // require AAE in credential, default: false
  evaluateAction?: string;     // URI of action to evaluate against AAE
  evaluateAmount?: number;     // transaction amount for threshold checks
  evaluateJurisdiction?: string; // ISO 3166-1 alpha-2
  onUnauthorized?: (reason: string) => void; // custom handler
  apiBase?: string;            // MolTrust API base URL, default: https://api.moltrust.ch
}

// Express augmentation
declare global {
  namespace Express {
    interface Request {
      agentVerification?: AgentVerification;
    }
  }
}
