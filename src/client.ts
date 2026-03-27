import type { AAE } from '@moltrust/aae';

const DEFAULT_API = 'https://api.moltrust.ch';

export interface TrustScoreResponse {
  did: string;
  trust_score: number;
  grade: string;
  withheld: boolean;
  flags?: string[];
  flag_count?: number;
}

export interface CredentialResponse {
  credentialId: string;
  authorizationEnvelope?: AAE;
}

export async function fetchTrustScore(
  did: string,
  apiBase = DEFAULT_API
): Promise<TrustScoreResponse> {
  const res = await fetch(`${apiBase}/skill/trust-score/${encodeURIComponent(did)}`);
  if (!res.ok) throw new Error(`Trust score fetch failed: ${res.status}`);
  return res.json() as Promise<TrustScoreResponse>;
}

export async function fetchCredentialAAE(
  credentialId: string,
  apiBase = DEFAULT_API
): Promise<AAE | undefined> {
  try {
    const res = await fetch(`${apiBase}/vc/aae/info?credentialId=${encodeURIComponent(credentialId)}`);
    if (!res.ok) return undefined;
    const data = await res.json() as Record<string, any>;
    return data.authorizationEnvelope;
  } catch {
    return undefined;
  }
}
