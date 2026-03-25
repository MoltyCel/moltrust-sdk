// Extract agent DID and credential from request headers/body
// Convention:
//   X-Agent-DID: did:moltrust:agent042
//   X-Agent-Credential: <credentialId>
//   Authorization: Bearer <did> (fallback)

export interface ExtractedAgent {
  did: string | null;
  credentialId: string | null;
}

export function extractFromHeaders(headers: Record<string, string | string[] | undefined>): ExtractedAgent {
  const did =
    (headers['x-agent-did'] as string) ||
    (headers['x-moltrust-did'] as string) ||
    extractBearerDid(headers['authorization'] as string) ||
    null;

  const credentialId =
    (headers['x-agent-credential'] as string) ||
    (headers['x-moltrust-credential'] as string) ||
    null;

  return { did, credentialId };
}

function extractBearerDid(auth?: string): string | null {
  if (!auth?.startsWith('Bearer did:')) return null;
  return auth.slice(7); // Remove "Bearer "
}
