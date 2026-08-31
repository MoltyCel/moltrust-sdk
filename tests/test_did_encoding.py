"""M8 — the DID goes into the path encoded, so it cannot alter the request path."""
from urllib.parse import quote

import pytest


HOSTILE = [
    "did:moltrust:../../admin/keys",
    "did:web:example.com/../../etc",
    "did:moltrust:abc?admin=1",
    "did:moltrust:abc#frag",
    "did:moltrust:a b",
]


def test_quote_escapes_every_path_altering_character():
    for did in HOSTILE:
        encoded = quote(did, safe="")
        assert "/" not in encoded, did
        assert "?" not in encoded, did
        assert "#" not in encoded, did
        assert " " not in encoded, did


def test_ordinary_dids_survive_encoding():
    did = "did:moltrust:d34ed796a4dc4698"
    assert quote(did, safe="") == "did%3Amoltrust%3Ad34ed796a4dc4698"
