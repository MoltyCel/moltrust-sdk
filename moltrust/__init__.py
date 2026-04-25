"""MolTrust SDK - Trust Layer for the Agent Economy"""

from moltrust.client import MolTrust, AsyncMolTrust, MolTrustError
from moltrust.models import (
    Agent,
    Credential,
    Reputation,
    VerificationResult,
    DIDDocument,
    ResolutionResult,
    ResolutionError,
)
from moltrust.resolver import MolTrustResolver, AsyncMolTrustResolver

__version__ = "0.2.0"
__all__ = [
    # Client
    "MolTrust",
    "AsyncMolTrust",
    "MolTrustError",
    # Models
    "Agent",
    "Credential",
    "Reputation",
    "VerificationResult",
    "DIDDocument",
    "ResolutionResult",
    "ResolutionError",
    # Resolver
    "MolTrustResolver",
    "AsyncMolTrustResolver",
]
