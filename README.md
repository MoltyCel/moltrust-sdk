# @moltrust/sdk

Verify AI agent trust scores in 3 lines of code.

```typescript
import { AgentTrust } from '@moltrust/sdk';

const result = await AgentTrust.verify('did:moltrust:abc123');
if (!result.verified) throw new Error(result.reason);
```

## Install

```bash
npm install @moltrust/sdk
```

## Standalone Verification

```typescript
import { AgentTrust } from '@moltrust/sdk';

// Simple check
const result = await AgentTrust.verify('did:moltrust:abc123');
console.log(result.verified);    // true/false
console.log(result.trustScore);  // 0-100
console.log(result.grade);       // "A" | "B" | "C" | "D" | "F"
console.log(result.flags);       // [] or ['low_confidence', ...]

// With minimum score
const result = await AgentTrust.verify('did:moltrust:abc123', {
  minScore: 70,
});

// Block specific flags
const result = await AgentTrust.verify('did:moltrust:abc123', {
  minScore: 50,
  blockFlags: ['young_endorser_cluster', 'score_drop_anomaly'],
});
```

### VerificationResult

```typescript
{
  verified: boolean;     // true if all checks passed
  did: string;
  trustScore: number;    // 0-100
  grade: string;         // "A" | "B" | "C" | "D" | "F"
  flags: string[];       // anomaly flags (empty = clean)
  reason?: string;       // why verified=false
  checkedAt: string;     // ISO timestamp
}
```

## Express Middleware

```typescript
import express from 'express';
import { AgentTrust } from '@moltrust/sdk';

const app = express();

// Reads DID from X-Agent-DID header, returns 403 if score < 70
app.use('/api/action', AgentTrust.middleware({ minScore: 70 }));

// Block specific anomaly flags
app.use('/api/payment', AgentTrust.middleware({
  minScore: 60,
  blockFlags: ['young_endorser_cluster'],
}));

// Access verification result in handler
app.post('/api/action', (req, res) => {
  const trust = req.agentVerification;
  console.log(trust?.did, trust?.trustScore, trust?.flags);
  res.json({ ok: true });
});
```

## Hono Middleware

```typescript
import { Hono } from 'hono';
import { AgentTrust } from '@moltrust/sdk';

const app = new Hono();
app.use('/api/action', AgentTrust.honoMiddleware({ minScore: 70 }));
```

## AAE Evaluation

The middleware can evaluate Agent Authorization Envelopes:

```typescript
app.use('/api/purchase', AgentTrust.middleware({
  minScore: 50,
  requireAAE: true,
  evaluateAction: 'commerce/purchase',
  evaluateAmount: 500,
}));
```

## Register an Agent

```typescript
const agent = await AgentTrust.register({
  displayName: 'My Trading Agent',
  apiKey: process.env.MOLTRUST_API_KEY!,
});
// { did: 'did:moltrust:...', ... }
```

## Trust Flags

Flags signal behavioral anomalies. They are informational for verifiers — no score deduction:

| Flag | Trigger |
|---|---|
| `repetitive_endorsements` | >80% of endorsements to one DID |
| `low_confidence` | Active in only 1 vertical after 30+ days |
| `young_endorser_cluster` | Endorsed by >5 agents under 7 days old |
| `score_drop_anomaly` | Score dropped >20 points in 24h |

## Headers Convention

| Header | Purpose |
|---|---|
| `X-Agent-DID` | Agent's MolTrust DID (primary) |
| `X-Agent-Credential` | Credential ID for AAE lookup |
| `Authorization: Bearer did:...` | Fallback DID extraction |

Full docs: https://moltrust.ch/developers
