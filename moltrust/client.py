"""MolTrust API client."""

import httpx
from typing import Optional, Dict, Any, Union
from urllib.parse import quote
from moltrust.models import Agent, Credential, Reputation, VerificationResult


class MolTrustError(Exception):
    def __init__(self, message: str, status_code: int = 0, detail: Any = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(message)


class MolTrust:
    DEFAULT_URL = "https://api.moltrust.ch"

    def __init__(self, api_key: str, base_url: str = DEFAULT_URL, timeout: float = 15.0):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"X-API-Key": self.api_key, "Content-Type": "application/json", "User-Agent": "moltrust-python/0.1.0"},
            timeout=timeout,
        )

    def _handle_response(self, resp: httpx.Response) -> Dict[str, Any]:
        if resp.status_code == 429:
            raise MolTrustError("Rate limit exceeded", 429)
        if resp.status_code == 403:
            raise MolTrustError("Invalid API key", 403)
        if resp.status_code >= 400:
            detail = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text
            raise MolTrustError(f"API error: {resp.status_code}", resp.status_code, detail)
        return resp.json()

    def register(self, display_name: str, platform: str = "moltrust") -> Agent:
        data = self._handle_response(self._client.post("/identity/register", json={"display_name": display_name, "platform": platform}))
        return Agent(did=data["did"], display_name=data["display_name"], status=data.get("status", "registered"))

    def verify(self, did: str) -> bool:
        data = self._handle_response(self._client.get(f"/identity/verify/{quote(did, safe='')}"))
        return data.get("verified", False)

    def resolve(self, did: str) -> Dict[str, Any]:
        return self._handle_response(self._client.get(f"/identity/resolve/{quote(did, safe='')}"))

    def get_reputation(self, did: str) -> Reputation:
        data = self._handle_response(self._client.get(f"/reputation/query/{quote(did, safe='')}"))
        return Reputation(did=data["did"], score=data["score"], total_ratings=data["total_ratings"])

    def rate(self, from_did: str, to_did: str, score: int) -> Dict[str, Any]:
        if not 1 <= score <= 5:
            raise ValueError("Score must be between 1 and 5")
        if from_did == to_did:
            raise ValueError("Cannot rate yourself")
        return self._handle_response(self._client.post("/reputation/rate", json={"from_did": from_did, "to_did": to_did, "score": score}))

    def issue_credential(self, subject_did: str, credential_type: str = "AgentTrustCredential") -> Credential:
        data = self._handle_response(self._client.post("/credentials/issue", json={"subject_did": subject_did, "credential_type": credential_type}))
        return Credential.from_dict(data)

    def verify_credential(self, credential: Union[Credential, Dict]) -> VerificationResult:
        cred_dict = credential.to_dict() if isinstance(credential, Credential) else credential
        data = self._handle_response(self._client.post("/credentials/verify", json={"credential": cred_dict}))
        return VerificationResult(valid=data.get("valid", False), issuer=data.get("issuer"), subject=data.get("subject"), error=data.get("error"))

    def did_document(self) -> Dict[str, Any]:
        return self._handle_response(self._client.get("/.well-known/did.json"))

    def health(self) -> Dict[str, Any]:
        return self._handle_response(self._client.get("/health"))

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._client.close()

    def close(self):
        self._client.close()


class AsyncMolTrust:
    def __init__(self, api_key: str, base_url: str = MolTrust.DEFAULT_URL, timeout: float = 15.0):
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            headers={"X-API-Key": api_key, "Content-Type": "application/json", "User-Agent": "moltrust-python/0.1.0"},
            timeout=timeout,
        )

    def _handle_response(self, resp: httpx.Response) -> Dict[str, Any]:
        if resp.status_code == 429:
            raise MolTrustError("Rate limit exceeded", 429)
        if resp.status_code == 403:
            raise MolTrustError("Invalid API key", 403)
        if resp.status_code >= 400:
            detail = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text
            raise MolTrustError(f"API error: {resp.status_code}", resp.status_code, detail)
        return resp.json()

    async def register(self, display_name: str, platform: str = "moltrust") -> Agent:
        data = self._handle_response(await self._client.post("/identity/register", json={"display_name": display_name, "platform": platform}))
        return Agent(did=data["did"], display_name=data["display_name"], status=data.get("status", "registered"))

    async def verify(self, did: str) -> bool:
        return self._handle_response(await self._client.get(f"/identity/verify/{quote(did, safe='')}")).get("verified", False)

    async def resolve(self, did: str) -> Dict[str, Any]:
        return self._handle_response(await self._client.get(f"/identity/resolve/{quote(did, safe='')}"))

    async def get_reputation(self, did: str) -> Reputation:
        data = self._handle_response(await self._client.get(f"/reputation/query/{quote(did, safe='')}"))
        return Reputation(did=data["did"], score=data["score"], total_ratings=data["total_ratings"])

    async def rate(self, from_did: str, to_did: str, score: int) -> Dict[str, Any]:
        return self._handle_response(await self._client.post("/reputation/rate", json={"from_did": from_did, "to_did": to_did, "score": score}))

    async def issue_credential(self, subject_did: str, credential_type: str = "AgentTrustCredential") -> Credential:
        data = self._handle_response(await self._client.post("/credentials/issue", json={"subject_did": subject_did, "credential_type": credential_type}))
        return Credential.from_dict(data)

    async def verify_credential(self, credential: Union[Credential, Dict]) -> VerificationResult:
        cred_dict = credential.to_dict() if isinstance(credential, Credential) else credential
        data = self._handle_response(await self._client.post("/credentials/verify", json={"credential": cred_dict}))
        return VerificationResult(valid=data.get("valid", False), issuer=data.get("issuer"), subject=data.get("subject"), error=data.get("error"))

    async def health(self) -> Dict[str, Any]:
        return self._handle_response(await self._client.get("/health"))

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self._client.aclose()
