# moltrust

[![PyPI](https://img.shields.io/pypi/v/moltrust.svg)](https://pypi.org/project/moltrust/)
[![Python](https://img.shields.io/pypi/pyversions/moltrust.svg)](https://pypi.org/project/moltrust/)
[![License](https://img.shields.io/pypi/l/moltrust.svg)](LICENSE)

DID resolver and trust layer for the agent economy. Python + TypeScript SDKs for `did:moltrust:*` and `did:web:*` resolution against [api.moltrust.ch](https://api.moltrust.ch).

## What is MolTrust?

MolTrust resolves W3C Decentralized Identifiers (DIDs) for autonomous agents and exposes trust scores, verifiable credentials, and reputation signals through a single API. It is operated by [CryptoKRI GmbH, Zürich](https://moltrust.ch).

This package ships two SDKs:
- **Python** (`pip install moltrust`) — primary, includes the DID resolver
- **TypeScript** (`npm install @moltrust/sdk`) — standalone trust verification

---

## Quick Start (Python)

```bash
pip install moltrust
```

Resolve a DID:

```python
from moltrust import MolTrustResolver

with MolTrustResolver() as resolver:
    doc = resolver.resolve("did:moltrust:d34ed796a4dc4698")
    print(doc.id)
    # did:moltrust:d34ed796a4dc4698
```

Async variant:

```python
from moltrust import AsyncMolTrustResolver

async with AsyncMolTrustResolver() as resolver:
    doc = await resolver.resolve("did:web:api.moltrust.ch")
    print(doc.id)
```

Use as a drop-in resolver for any DID-aware harness that accepts the W3C resolution Protocol:

```python
from moltrust import MolTrustResolver

# Constructor injection: any harness that accepts a `resolve(did) -> DIDDocument`
# Protocol can use MolTrustResolver as-is.
harness = SomeHarness(resolver=MolTrustResolver())
```

### Supported DID Methods

| Method                | Status | Notes |
|-----------------------|--------|-------|
| `did:moltrust:*`      | ✅ Native | Including bridge-resolved `did:moltrust:ext_*` |
| `did:web:*`           | ✅ Native | Resolved via the MolTrust API or directly per W3C spec |
| `did:agentnexus:*`    | 🔜 Roadmap | Bridge-resolution path planned |
| `did:meeet:*`         | 🔜 Roadmap | Bridge-resolution path planned |
| `did:key:*`           | ❌ Out of scope | Use a `did:key` resolver such as `didkit-py` |
| Other                 | `methodNotSupported` | Caller can fall back to a different resolver |

### Errors

`MolTrustResolver.resolve()` raises `ResolutionError` with a `reason` attribute matching the W3C error codes:

| Reason              | When |
|---------------------|------|
| `methodNotSupported`| DID method not handled by this resolver |
| `notFound`          | DID syntactically valid, no document found |
| `invalidDid`        | Malformed DID input |
| `didNotResolved`    | Network error, malformed response, etc. |

### Other Python APIs

```python
from moltrust import MolTrust, AsyncMolTrust

with MolTrust(api_key="mt_...") as mt:
    agent = mt.register("My Agent")
    rep = mt.get_reputation(agent.did)
    cred = mt.issue_credential(agent.did)
```

See `moltrust.client.MolTrust` for the full client API.

---

## Quick Start (TypeScript)

```bash
npm install @moltrust/sdk
```

```typescript
import { AgentTrust } from '@moltrust/sdk';

const result = await AgentTrust.verify('did:moltrust:abc123');
if (!result.verified) throw new Error(result.reason);
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

### Express Middleware

```typescript
import express from 'express';
import { AgentTrust } from '@moltrust/sdk';

const app = express();

app.use('/api/action', AgentTrust.middleware({ minScore: 70 }));

app.post('/api/action', (req, res) => {
  const trust = req.agentVerification;
  res.json({ ok: true, trust });
});
```

### Hono Middleware

```typescript
import { Hono } from 'hono';
import { agentTrust } from '@moltrust/sdk/hono';

const app = new Hono();
app.use('/secure/*', agentTrust({ minScore: 60 }));
```

### Trust Flags

Informational anomaly signals — no score deduction:

| Flag | Trigger |
|---|---|
| `repetitive_endorsements` | >80% of endorsements to one DID |
| `low_confidence` | Active in only 1 vertical after 30+ days |
| `young_endorser_cluster` | Endorsed by >5 agents under 7 days old |
| `score_drop_anomaly` | Score dropped >20 points in 24h |

### Headers Convention

| Header | Purpose |
|---|---|
| `X-Agent-DID` | Agent's MolTrust DID (primary) |
| `X-Agent-Credential` | Credential ID for AAE lookup |
| `Authorization: Bearer did:...` | Fallback DID extraction |

---

## Used By

- [aeoess/a2a-compliance-harness](https://github.com/aeoess/a2a-compliance-harness) — A2A protocol compliance probing (drop-in via constructor injection)

## License

MIT — see [LICENSE](LICENSE).

Full developer docs: https://moltrust.ch/developers
Open issues: https://github.com/MoltyCel/moltrust-sdk/issues
