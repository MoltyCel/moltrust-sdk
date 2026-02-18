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
