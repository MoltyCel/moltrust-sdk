import { extractFromHeaders } from './extract';

jest.setTimeout(15000);

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

describe('AgentTrust.verify() standalone', () => {
  const { AgentTrust } = require('./agent-trust');

  test('verify known good agent — TrustScout', async () => {
    const result = await AgentTrust.verify('did:moltrust:d34ed796a4dc4698');
    expect(result.did).toBe('did:moltrust:d34ed796a4dc4698');
    expect(typeof result.trustScore).toBe('number');
    expect(result.trustScore).toBeGreaterThan(0);
    expect(result.verified).toBe(true);
    expect(Array.isArray(result.flags)).toBe(true);
    expect(result.checkedAt).toBeTruthy();
  });

  test('verify with minScore — pass', async () => {
    const result = await AgentTrust.verify('did:moltrust:d34ed796a4dc4698', { minScore: 50 });
    expect(result.verified).toBe(true);
  });

  test('verify with minScore — fail', async () => {
    const result = await AgentTrust.verify('did:moltrust:d34ed796a4dc4698', { minScore: 99 });
    expect(result.verified).toBe(false);
    expect(result.reason).toContain('below minimum');
  });

  test('verify nonexistent DID — withheld', async () => {
    const result = await AgentTrust.verify('did:moltrust:doesnotexist999');
    expect(result.verified).toBe(false);
    expect(result.trustScore).toBe(0);
    expect(result.reason).toContain('withheld');
  });

  test('blockFlags blocks agent with matching flag', async () => {
    // TrustScout has repetitive_endorsements flag
    const result = await AgentTrust.verify('did:moltrust:d34ed796a4dc4698', {
      blockFlags: ['repetitive_endorsements'],
    });
    expect(result.verified).toBe(false);
    expect(result.reason).toContain('repetitive_endorsements');
  });

  test('blockFlags allows agent without matching flag', async () => {
    const result = await AgentTrust.verify('did:moltrust:d34ed796a4dc4698', {
      blockFlags: ['score_drop_anomaly'],
    });
    expect(result.verified).toBe(true);
  });

  test('returns flags array from API', async () => {
    const result = await AgentTrust.verify('did:moltrust:d34ed796a4dc4698');
    expect(result.flags).toContain('repetitive_endorsements');
  });
});

describe('AgentTrust middleware interface', () => {
  test('exports middleware function', () => {
    const { AgentTrust } = require('./agent-trust');
    const mw = AgentTrust.middleware({ minScore: 50 });
    expect(typeof mw).toBe('function');
  });

  test('exports honoMiddleware function', () => {
    const { AgentTrust } = require('./agent-trust');
    const mw = AgentTrust.honoMiddleware({ minScore: 50 });
    expect(typeof mw).toBe('function');
  });
});
