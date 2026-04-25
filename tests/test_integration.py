"""Integration tests for MolTrust SDK."""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from moltrust import MolTrust
from moltrust.client import MolTrustError

API_KEY = os.getenv("MOLTRUST_API_KEY", "")
BASE_URL = os.getenv("MOLTRUST_API_URL", "https://api.moltrust.ch")

def test_full_flow():
    mt = MolTrust(api_key=API_KEY, base_url=BASE_URL)

    health = mt.health()
    assert health["status"] == "ok"
    print(f"  Health: {health['status']} (v{health['version']})")

    agent = mt.register("SDK_Test_Agent")
    assert agent.did.startswith("did:moltrust:")
    print(f"  Register: {agent}")

    is_verified = mt.verify(agent.did)
    assert is_verified is True
    print(f"  Verify: {is_verified}")

    doc = mt.resolve(agent.did)
    assert doc["id"] == agent.did
    print(f"  Resolve: {doc['id']}")

    vc = mt.issue_credential(agent.did)
    assert vc.issuer == "did:web:api.moltrust.ch"
    assert vc.is_signed
    print(f"  Issue VC: {vc}")

    result = mt.verify_credential(vc)
    assert result.valid is True
    print(f"  Verify VC: {result}")

    rep = mt.get_reputation(agent.did)
    assert rep.did == agent.did
    print(f"  Reputation: {rep}")

    did_doc = mt.did_document()
    assert did_doc["id"] == "did:web:api.moltrust.ch"
    print(f"  DID Document: {did_doc['id']}")

    try:
        bad_mt = MolTrust(api_key="wrong_key", base_url=BASE_URL)
        bad_mt.register("ShouldFail")
        assert False
    except MolTrustError as e:
        assert e.status_code == 403
        print(f"  Auth error handled: {e.message}")

    mt.close()
    print("\nAll tests passed!")

if __name__ == "__main__":
    test_full_flow()
