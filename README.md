# MolTrust SDK

**Trust Layer for the Agent Economy.**

MolTrust provides identity verification, reputation scoring, and W3C Verifiable Credentials for AI agents.

## Install
```bash
pip install moltrust
```

## Quickstart
```python
from moltrust import MolTrust

mt = MolTrust(api_key="mt_your_key")

# Register an agent
agent = mt.register("MyAgent")
print(agent.did)  # did:moltrust:a1b2c3d4...

# Issue a Verifiable Credential
vc = mt.issue_credential(agent.did)
print(vc.is_signed)  # True

# Verify the credential
result = mt.verify_credential(vc)
print(result.valid)  # True
```

## Features

- **Identity** — Register, verify, and resolve agent DIDs
- **Reputation** — Rate agents and query trust scores
- **Verifiable Credentials** — Issue and verify W3C VCs with Ed25519 signatures
- **Async Support** — Full async client via `AsyncMolTrust`

## Integration Examples

### LangChain Tool
```python
from langchain.tools import tool
from moltrust import MolTrust

mt = MolTrust(api_key="mt_...")

@tool
def verify_agent(did: str) -> str:
    """Verify if an AI agent is trusted via MolTrust."""
    if mt.verify(did):
        rep = mt.get_reputation(did)
        return f"Verified. Trust score: {rep.score}/5 ({rep.total_ratings} ratings)"
    return "Agent not found."
```

### Pre-Transaction Check
```python
mt = MolTrust(api_key="mt_...")

def safe_transact(counterparty_did: str):
    rep = mt.get_reputation(counterparty_did)
    if not rep.is_trusted:
        raise Exception(f"Not trusted (score: {rep.score})")
    vc = mt.issue_credential(counterparty_did, "TransactionCredential")
    return vc
```

## Standards

- **W3C DID:web** — Decentralized Identifiers
- **W3C Verifiable Credentials** — Tamper-proof credentials
- **Ed25519** — Elliptic curve signatures
- **Lightning Network** — Bitcoin L2 payments

## Links

- **API Docs:** https://api.moltrust.ch/docs
- **DID Document:** https://api.moltrust.ch/.well-known/did.json
- **Website:** https://moltrust.ch
- **X:** [@moltrust](https://x.com/moltrust)

## License

MIT — CryptoKRI GmbH, Zurich, Switzerland
