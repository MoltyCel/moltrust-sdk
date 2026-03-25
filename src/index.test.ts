import { extractFromHeaders } from './extract';

describe('extractFromHeaders()', () => {
  test('extracts DID from x-agent-did header', () => {
    const result = extractFromHeaders({ 'x-agent-did': 'did:moltrust:agent042' });
    expect(result.did).toBe('did:moltrust:agent042');
  });

  test('extracts credential from x-agent-credential header', () => {
    const result = extractFromHeaders({ 'x-agent-credential': 'cred-123' });
    expect(result.credentialId).toBe('cred-123');
  });

  test('extracts DID from Bearer token', () => {
    const result = extractFromHeaders({ 'authorization': 'Bearer did:moltrust:agent042' });
    expect(result.did).toBe('did:moltrust:agent042');
  });

  test('returns null when no DID present', () => {
    const result = extractFromHeaders({ 'content-type': 'application/json' });
    expect(result.did).toBeNull();
  });

  test('x-agent-did takes precedence over Authorization', () => {
    const result = extractFromHeaders({
      'x-agent-did': 'did:moltrust:agent001',
      'authorization': 'Bearer did:moltrust:agent002'
    });
    expect(result.did).toBe('did:moltrust:agent001');
  });
});

describe('AgentTrust.verify() interface', () => {
  test('exports verify function', () => {
    const { verify } = require('./middleware');
    expect(typeof verify).toBe('function');
    expect(typeof verify({})).toBe('function');
  });

  test('exports honoVerify function', () => {
    const { honoVerify } = require('./hono');
    expect(typeof honoVerify).toBe('function');
    expect(typeof honoVerify({})).toBe('function');
  });
});
