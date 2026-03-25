# @moltrust/sdk

MolTrust Agent Verification Middleware for Express, Hono, and Fastify.

## Install

```bash
npm install @moltrust/sdk
```

## Usage

### Express
```typescript
import express from 'express';
import { AgentTrust } from '@moltrust/sdk';

const app = express();

// Verify agent trust score (min 60)
app.use(AgentTrust.verify({ minScore: 60 }));

// Access verification result in route
app.get('/api/resource', (req, res) => {
  const { did, trustScore, grade } = req.agentVerification!;
  res.json({ message: `Hello agent ${did}, score: ${trustScore} (${grade})` });
});
```

### Hono
```typescript
import { Hono } from 'hono';
import { AgentTrust } from '@moltrust/sdk';

const app = new Hono();
app.use('*', AgentTrust.honoVerify({ minScore: 60 }));
```

### With AAE evaluation
```typescript
app.use('/api/purchase', AgentTrust.verify({
  minScore: 60,
  requireAAE: true,
  evaluateAction: 'https://api.example.com/purchase',
  evaluateAmount: 150,
  evaluateJurisdiction: 'CH',
}));
```

### Request headers
Agents must send:
```
X-Agent-DID: did:moltrust:agent042
X-Agent-Credential: <credentialId>  (optional, for AAE evaluation)
```

## Options

| Option | Type | Default | Description |
|---|---|---|---|
| minScore | number | 0 | Minimum trust score (0-100) |
| requireAAE | boolean | false | Require Agent Authorization Envelope |
| evaluateAction | string | -- | URI of action to evaluate against AAE |
| evaluateAmount | number | -- | Transaction amount for threshold checks |
| evaluateJurisdiction | string | -- | ISO 3166-1 alpha-2 country code |
| apiBase | string | https://api.moltrust.ch | MolTrust API base URL |

## req.agentVerification

```typescript
{
  did: string;
  trustScore: number;
  grade: string;           // S, A, B, C, D, F
  aae?: AAE;               // Agent Authorization Envelope
  aaeEvaluation?: {
    allowed: boolean;
    reason: string;
    requiresStepUp?: boolean;
    requiresHumanApproval?: boolean;
  };
  credentialId?: string;
  verified: boolean;
}
```
