"""DID resolver for MolTrust.

Resolves did:moltrust:* (native + bridge-resolved ext_*) and did:web:* DIDs
via the MolTrust API. Other DID methods raise ResolutionError("methodNotSupported").

Designed as a drop-in DID resolver matching the protocol used by
aeoess/a2a-compliance-harness::

    from moltrust import MolTrustResolver

    with MolTrustResolver() as resolver:
        doc = resolver.resolve("did:moltrust:d34ed796a4dc4698")
        print(doc.id)
"""

import re
from typing import Optional

import httpx

from moltrust.models import DIDDocument, ResolutionError


DEFAULT_API_URL = "https://api.moltrust.ch"
DEFAULT_TIMEOUT = 5.0
USER_AGENT = "moltrust-python/0.2.0"

# Methods this resolver natively handles
SUPPORTED_METHODS = ("moltrust", "web")

# Pattern matching the DID syntax we accept
_DID_PREFIX = re.compile(r"^did:([a-z0-9]+):")


def _validate_did_syntax(did: str) -> str:
    """Return the lowercase method name if `did` looks like a valid DID.

    Raises ResolutionError(invalidDid) on syntax problems.
    """
    if not isinstance(did, str) or not did:
        raise ResolutionError("invalidDid", did or "", detail="empty input")
    if len(did) > 256:
        raise ResolutionError("invalidDid", did, detail="DID too long (>256 chars)")
    m = _DID_PREFIX.match(did)
    if not m:
        raise ResolutionError("invalidDid", did, detail="missing did:<method>: prefix")
    method = m.group(1)
    # method-specific-id must be non-empty
    rest = did[m.end():]
    if not rest:
        raise ResolutionError("invalidDid", did, detail="missing method-specific identifier")
    return method


class MolTrustResolver:
    """Synchronous DID resolver that calls api.moltrust.ch.

    Args:
        api_url: Base URL of the MolTrust API. Defaults to https://api.moltrust.ch.
        timeout: HTTP timeout in seconds for the resolve call. Default 5.0.
        http_client: Optional pre-configured httpx.Client. If provided, the
            resolver does not own its lifecycle (close() is a no-op).

    Example:
        >>> with MolTrustResolver() as r:
        ...     doc = r.resolve("did:moltrust:d34ed796a4dc4698")
        ...     assert doc.id == "did:moltrust:d34ed796a4dc4698"
    """

    SUPPORTED_METHODS = SUPPORTED_METHODS

    def __init__(
        self,
        api_url: str = DEFAULT_API_URL,
        timeout: float = DEFAULT_TIMEOUT,
        http_client: Optional[httpx.Client] = None,
    ):
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout
        self._owns_client = http_client is None
        self._client = http_client or httpx.Client(
            timeout=timeout,
            headers={"User-Agent": USER_AGENT, "Accept": "application/did+ld+json, application/json"},
        )

    def resolve(self, did: str) -> DIDDocument:
        """Resolve a DID to a DIDDocument.

        Raises:
            ResolutionError: with reason in
                {methodNotSupported, notFound, invalidDid, didNotResolved}.
        """
        method = _validate_did_syntax(did)
        if method not in self.SUPPORTED_METHODS:
            raise ResolutionError(
                "methodNotSupported",
                did,
                detail=f"resolver supports {self.SUPPORTED_METHODS}, got did:{method}:",
            )
        # Both did:moltrust:* and did:web:* go through MolTrust API path-style.
        # /identity/resolve handles did:moltrust natively and proxies did:web
        # via Phase-2 backend support.
        url = f"{self.api_url}/identity/resolve/{did}"
        try:
            resp = self._client.get(url)
        except httpx.RequestError as exc:
            raise ResolutionError(
                "didNotResolved",
                did,
                detail=f"network error: {exc.__class__.__name__}",
            ) from exc

        if resp.status_code == 404:
            raise ResolutionError("notFound", did, http_status=404)
        if resp.status_code == 400:
            # Backend reports unsupported method — surface as such
            raise ResolutionError(
                "methodNotSupported",
                did,
                http_status=400,
                detail=resp.text[:200] if resp.text else "",
            )
        if resp.status_code != 200:
            raise ResolutionError(
                "didNotResolved",
                did,
                http_status=resp.status_code,
                detail=resp.text[:200] if resp.text else "",
            )
        try:
            data = resp.json()
        except ValueError as exc:
            raise ResolutionError(
                "didNotResolved",
                did,
                detail=f"invalid JSON: {exc}",
            ) from exc
        if not isinstance(data, dict) or not data.get("id"):
            raise ResolutionError(
                "didNotResolved",
                did,
                detail="response missing 'id' field",
            )
        return DIDDocument.from_dict(data)

    def close(self) -> None:
        if self._owns_client and self._client is not None:
            self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class AsyncMolTrustResolver:
    """Async variant of MolTrustResolver. See MolTrustResolver for details.

    Example:
        >>> async with AsyncMolTrustResolver() as r:
        ...     doc = await r.resolve("did:moltrust:d34ed796a4dc4698")
    """

    SUPPORTED_METHODS = SUPPORTED_METHODS

    def __init__(
        self,
        api_url: str = DEFAULT_API_URL,
        timeout: float = DEFAULT_TIMEOUT,
        http_client: Optional[httpx.AsyncClient] = None,
    ):
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout
        self._owns_client = http_client is None
        self._client = http_client or httpx.AsyncClient(
            timeout=timeout,
            headers={"User-Agent": USER_AGENT, "Accept": "application/did+ld+json, application/json"},
        )

    async def resolve(self, did: str) -> DIDDocument:
        method = _validate_did_syntax(did)
        if method not in self.SUPPORTED_METHODS:
            raise ResolutionError(
                "methodNotSupported",
                did,
                detail=f"resolver supports {self.SUPPORTED_METHODS}, got did:{method}:",
            )
        url = f"{self.api_url}/identity/resolve/{did}"
        try:
            resp = await self._client.get(url)
        except httpx.RequestError as exc:
            raise ResolutionError(
                "didNotResolved",
                did,
                detail=f"network error: {exc.__class__.__name__}",
            ) from exc

        if resp.status_code == 404:
            raise ResolutionError("notFound", did, http_status=404)
        if resp.status_code == 400:
            raise ResolutionError(
                "methodNotSupported",
                did,
                http_status=400,
                detail=resp.text[:200] if resp.text else "",
            )
        if resp.status_code != 200:
            raise ResolutionError(
                "didNotResolved",
                did,
                http_status=resp.status_code,
                detail=resp.text[:200] if resp.text else "",
            )
        try:
            data = resp.json()
        except ValueError as exc:
            raise ResolutionError(
                "didNotResolved",
                did,
                detail=f"invalid JSON: {exc}",
            ) from exc
        if not isinstance(data, dict) or not data.get("id"):
            raise ResolutionError(
                "didNotResolved",
                did,
                detail="response missing 'id' field",
            )
        return DIDDocument.from_dict(data)

    async def aclose(self) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.aclose()
