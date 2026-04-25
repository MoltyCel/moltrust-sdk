"""MolTrust data models."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List


@dataclass
class Agent:
    did: str
    display_name: str
    platform: str = "moltrust"
    status: str = "registered"

    def __repr__(self):
        return f"Agent(did='{self.did}', name='{self.display_name}')"


@dataclass
class Reputation:
    did: str
    score: float
    total_ratings: int

    @property
    def is_trusted(self) -> bool:
        return self.score >= 3.0 and self.total_ratings >= 3

    def __repr__(self):
        return f"Reputation(did='{self.did}', score={self.score}, ratings={self.total_ratings})"


@dataclass
class Credential:
    context: List[str]
    type: List[str]
    issuer: str
    issuance_date: str
    expiration_date: str
    subject: Dict[str, Any]
    proof: Dict[str, str]
    _raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @property
    def subject_did(self) -> str:
        return self.subject.get("id", "")

    @property
    def is_signed(self) -> bool:
        return bool(self.proof.get("proofValue"))

    def to_dict(self) -> Dict[str, Any]:
        return self._raw

    def __repr__(self):
        return f"Credential(type={self.type}, subject=\'{self.subject_did}\')"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Credential":
        return cls(
            context=data.get("@context", []),
            type=data.get("type", []),
            issuer=data.get("issuer", ""),
            issuance_date=data.get("issuanceDate", ""),
            expiration_date=data.get("expirationDate", ""),
            subject=data.get("credentialSubject", {}),
            proof=data.get("proof", {}),
            _raw=data,
        )


@dataclass
class VerificationResult:
    valid: bool
    issuer: Optional[str] = None
    subject: Optional[str] = None
    error: Optional[str] = None

    def __repr__(self):
        if self.valid:
            return f"VerificationResult(valid=True, subject=\'{self.subject}\')"
        return f"VerificationResult(valid=False, error=\'{self.error}\')"

    def __bool__(self):
        return self.valid


@dataclass
class DIDDocument:
    """W3C DID Document.

    Minimal subset matching the W3C DID Core spec:
    https://www.w3.org/TR/did-core/#did-document-properties
    """
    id: str
    context: List[str] = field(default_factory=list)
    controller: Optional[str] = None
    verification_method: List[Dict[str, Any]] = field(default_factory=list)
    authentication: List[str] = field(default_factory=list)
    assertion_method: List[str] = field(default_factory=list)
    service: List[Dict[str, Any]] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    def __repr__(self):
        return f"DIDDocument(id='{self.id}', verification_methods={len(self.verification_method)})"

    def to_dict(self) -> Dict[str, Any]:
        """Return the original raw document if available, otherwise reconstruct."""
        if self.raw:
            return self.raw
        out: Dict[str, Any] = {
            "@context": self.context,
            "id": self.id,
        }
        if self.controller is not None:
            out["controller"] = self.controller
        if self.verification_method:
            out["verificationMethod"] = self.verification_method
        if self.authentication:
            out["authentication"] = self.authentication
        if self.assertion_method:
            out["assertionMethod"] = self.assertion_method
        if self.service:
            out["service"] = self.service
        return out

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DIDDocument":
        """Build from a JSON-LD DID Document dict.

        Accepts both `@context` (W3C) and `context` field names.
        """
        ctx = data.get("@context", data.get("context", []))
        if isinstance(ctx, str):
            ctx = [ctx]
        return cls(
            id=data.get("id", ""),
            context=list(ctx) if ctx else [],
            controller=data.get("controller"),
            verification_method=list(data.get("verificationMethod", [])),
            authentication=list(data.get("authentication", [])),
            assertion_method=list(data.get("assertionMethod", [])),
            service=list(data.get("service", [])),
            raw=dict(data),
        )


@dataclass
class ResolutionResult:
    """W3C DID Resolution result.

    Reference: https://www.w3.org/TR/did-core/#did-resolution
    """
    did_document: Optional[DIDDocument] = None
    did_resolution_metadata: Dict[str, Any] = field(default_factory=dict)
    did_document_metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_resolved(self) -> bool:
        return (
            self.did_document is not None
            and "error" not in self.did_resolution_metadata
        )

    @property
    def error(self) -> Optional[str]:
        return self.did_resolution_metadata.get("error")

    def __repr__(self):
        if self.is_resolved:
            return f"ResolutionResult(resolved, did='{self.did_document.id}')"
        return f"ResolutionResult(error='{self.error}')"


class ResolutionError(Exception):
    """Raised when DID resolution fails.

    Attributes mirror the W3C DID Resolution error codes:
      - methodNotSupported : DID method not supported by this resolver
      - notFound           : DID does not resolve to a document
      - invalidDid         : DID syntax is invalid
      - didNotResolved     : Network error, malformed response, etc.
    """

    def __init__(
        self,
        reason: str,
        did: str = "",
        http_status: Optional[int] = None,
        detail: str = "",
    ):
        self.reason = reason
        self.did = did
        self.http_status = http_status
        self.detail = detail
        msg = f"{reason}: {did}" if did else reason
        if http_status:
            msg += f" (HTTP {http_status})"
        if detail:
            msg += f" — {detail}"
        super().__init__(msg)
