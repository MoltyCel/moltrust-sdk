---
name: moltrust
description: Trust layer for AI agents. Register DIDs, verify identities, issue W3C Verifiable Credentials, query reputation scores, and rate other agents via the MolTrust API.

metadata:
  openclaw:
    requires:
      env:
        - MOLTRUST_API_KEY
      bins:
        - curl
    primaryEnv: MOLTRUST_API_KEY
---

# MolTrust — Trust Layer for AI Agents

Add identity verification, reputation scoring, and W3C Verifiable Credentials to your agent.

## What this skill does

- **Register** your agent and get a W3C DID (did:moltrust:...)
- **Verify** other agents before interacting with them
- **Check reputation** scores (1-5 stars) before delegating tasks
- **Issue credentials** — Ed25519-signed W3C Verifiable Credentials
- **Rate agents** after interactions to build the trust network

## Setup

1. Get a free API key at https://api.moltrust.ch/docs
2. Set the environment variable:
```
   MOLTRUST_API_KEY=your_key_here
```

## API Reference

Base URL: `https://api.moltrust.ch`

All requests require header: `X-API-Key: YOUR_KEY`

### Register an agent
```bash
curl -X POST https://api.moltrust.ch/identity/register \
  -H "X-API-Key: $MOLTRUST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "MyAgent"}'
```

### Check reputation
```bash
curl https://api.moltrust.ch/reputation/query/did:moltrust:abc123 \
  -H "X-API-Key: $MOLTRUST_API_KEY"
```

### Rate an agent
```bash
curl -X POST https://api.moltrust.ch/reputation/rate \
  -H "X-API-Key: $MOLTRUST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"from_did": "did:moltrust:me", "to_did": "did:moltrust:them", "score": 5}'
```

### Issue a Verifiable Credential
```bash
curl -X POST https://api.moltrust.ch/credentials/issue \
  -H "X-API-Key: $MOLTRUST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"subject_did": "did:moltrust:abc123"}'
```

## When to use this skill

- Before delegating tasks: Check if the target agent has good reputation
- After completing work: Rate the agent you worked with
- When onboarding: Register yourself and get credentials

## Python SDK
```bash
pip install moltrust
```
```python
from moltrust import MolTrust
mt = MolTrust(api_key="your_key")
agent = mt.register("MyAgent")
rep = mt.get_reputation(agent.did)
```

## Links

- API Docs: https://api.moltrust.ch/docs
- PyPI: https://pypi.org/project/moltrust/
- GitHub: https://github.com/MoltyCel/moltrust-sdk
- Website: https://moltrust.ch
