"""MolTrustResolver test suite.

Most tests run against the live MolTrust API at api.moltrust.ch.
Set MOLTRUST_API_URL to override the target.

Tests requiring network can be skipped with `pytest -m "not live"`.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from moltrust import (
    MolTrustResolver,
    AsyncMolTrustResolver,
    DIDDocument,
    ResolutionError,
)

API_URL = os.getenv("MOLTRUST_API_URL", "https://api.moltrust.ch")

TRUSTSCOUT_DID = "did:moltrust:d34ed796a4dc4698"
KEVIN_BRIDGE_DID = "did:moltrust:ext_516a656bafa39e5c"


# ── Pure unit tests (no network) ──────────────────────────────────────────────

def test_invalid_did_empty():
    with MolTrustResolver(api_url=API_URL) as r:
        with pytest.raises(ResolutionError) as exc:
            r.resolve("")
        assert exc.value.reason == "invalidDid"


def test_invalid_did_no_prefix():
    with MolTrustResolver(api_url=API_URL) as r:
        with pytest.raises(ResolutionError) as exc:
            r.resolve("not-a-did")
        assert exc.value.reason == "invalidDid"


def test_invalid_did_no_method_specific_id():
    with MolTrustResolver(api_url=API_URL) as r:
        with pytest.raises(ResolutionError) as exc:
            r.resolve("did:moltrust:")
        assert exc.value.reason == "invalidDid"


def test_invalid_did_too_long():
    with MolTrustResolver(api_url=API_URL) as r:
        with pytest.raises(ResolutionError) as exc:
            r.resolve("did:moltrust:" + "a" * 256)
        assert exc.value.reason == "invalidDid"


def test_unsupported_did_method_agentnexus():
    with MolTrustResolver(api_url=API_URL) as r:
        with pytest.raises(ResolutionError) as exc:
            r.resolve("did:agentnexus:z6MkhaXg")
        assert exc.value.reason == "methodNotSupported"


def test_unsupported_did_method_meeet():
    with MolTrustResolver(api_url=API_URL) as r:
        with pytest.raises(ResolutionError) as exc:
            r.resolve("did:meeet:test")
        assert exc.value.reason == "methodNotSupported"


def test_unsupported_did_method_key():
    with MolTrustResolver(api_url=API_URL) as r:
        with pytest.raises(ResolutionError) as exc:
            r.resolve("did:key:z6Mk")
        assert exc.value.reason == "methodNotSupported"


def test_supported_methods_constant():
    assert "moltrust" in MolTrustResolver.SUPPORTED_METHODS
    assert "web" in MolTrustResolver.SUPPORTED_METHODS
    assert "agentnexus" not in MolTrustResolver.SUPPORTED_METHODS


def test_resolution_error_attributes():
    err = ResolutionError("notFound", did="did:moltrust:abc", http_status=404)
    assert err.reason == "notFound"
    assert err.did == "did:moltrust:abc"
    assert err.http_status == 404
    assert "did:moltrust:abc" in str(err)


def test_did_document_to_from_dict_roundtrip():
    raw = {
        "@context": ["https://www.w3.org/ns/did/v1"],
        "id": "did:moltrust:abc1234567890def",
        "controller": "did:web:api.moltrust.ch",
        "verificationMethod": [{"id": "did:moltrust:abc#k1", "type": "Ed25519VerificationKey2020"}],
        "authentication": ["did:moltrust:abc#k1"],
        "assertionMethod": ["did:moltrust:abc#k1"],
    }
    doc = DIDDocument.from_dict(raw)
    assert doc.id == "did:moltrust:abc1234567890def"
    assert len(doc.verification_method) == 1
    # Round-trip preserves raw
    assert doc.to_dict() == raw


def test_custom_api_url():
    r = MolTrustResolver(api_url="https://example.invalid")
    assert r.api_url == "https://example.invalid"
    r.close()


def test_context_manager():
    with MolTrustResolver(api_url=API_URL) as r:
        assert r is not None
    # closing twice should not raise
    r.close()


# ── Live integration tests (require network + production API) ─────────────────


@pytest.mark.live
def test_resolve_native_moltrust_did_live():
    with MolTrustResolver(api_url=API_URL) as r:
        doc = r.resolve(TRUSTSCOUT_DID)
        assert isinstance(doc, DIDDocument)
        assert doc.id == TRUSTSCOUT_DID
        # TrustScout has a public key
        assert len(doc.verification_method) >= 1


@pytest.mark.live
def test_resolve_bridged_ext_did_live():
    """Phase-2 backend fix: ext_* bridge-DIDs now resolve."""
    with MolTrustResolver(api_url=API_URL) as r:
        doc = r.resolve(KEVIN_BRIDGE_DID)
        assert isinstance(doc, DIDDocument)
        assert doc.id == KEVIN_BRIDGE_DID


@pytest.mark.live
def test_resolve_did_web_self_live():
    with MolTrustResolver(api_url=API_URL) as r:
        doc = r.resolve("did:web:api.moltrust.ch")
        assert isinstance(doc, DIDDocument)
        assert doc.id == "did:web:api.moltrust.ch"
        # self-DID has the gateway verification method
        assert len(doc.verification_method) >= 1


@pytest.mark.live
def test_resolve_unknown_native_did_returns_not_found():
    with MolTrustResolver(api_url=API_URL) as r:
        with pytest.raises(ResolutionError) as exc:
            r.resolve("did:moltrust:0000000000000000")
        assert exc.value.reason == "notFound"


# ── Async variant smoke tests ─────────────────────────────────────────────────


@pytest.mark.asyncio
@pytest.mark.live
async def test_async_resolve_native_live():
    async with AsyncMolTrustResolver(api_url=API_URL) as r:
        doc = await r.resolve(TRUSTSCOUT_DID)
        assert doc.id == TRUSTSCOUT_DID


@pytest.mark.asyncio
async def test_async_unsupported_method():
    async with AsyncMolTrustResolver(api_url=API_URL) as r:
        with pytest.raises(ResolutionError) as exc:
            await r.resolve("did:agentnexus:z6Mk")
        assert exc.value.reason == "methodNotSupported"


# ── Protocol compliance ───────────────────────────────────────────────────────


def test_protocol_compliance_typing():
    """The resolver matches the typing.Protocol shape used in
    aeoess/a2a-compliance-harness:

        class DIDResolver(Protocol):
            def resolve(self, did: str) -> DIDDocument: ...
    """
    r = MolTrustResolver(api_url=API_URL)
    # Method exists with right signature
    assert callable(r.resolve)
    import inspect
    sig = inspect.signature(r.resolve)
    params = list(sig.parameters)
    assert params == ["did"]
    r.close()
