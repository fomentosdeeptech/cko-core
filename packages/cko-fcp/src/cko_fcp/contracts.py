"""Pure operation-envelope and capability/version contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ._validation import instant, optional_text, string_tuple, text
from .errors import CapabilityAbsentError, InvalidEnvelopeError, UnsupportedVersionError, ValidationError
from .models import FCPVersion


@dataclass(frozen=True, slots=True)
class PageRequest:
    page_size: int
    scope_fingerprint: str
    continuation: str | None = None

    def __post_init__(self) -> None:
        if type(self.page_size) is not int or not 1 <= self.page_size <= 1000:
            raise InvalidEnvelopeError("page_size must be an integer from 1 through 1000")
        object.__setattr__(self, "scope_fingerprint", text(self.scope_fingerprint, "scope_fingerprint", InvalidEnvelopeError))
        object.__setattr__(self, "continuation", optional_text(self.continuation, "continuation", InvalidEnvelopeError))


@dataclass(frozen=True, slots=True)
class OperationEnvelope:
    operation_id: str
    correlation_id: str
    fcp_version: FCPVersion
    requested_capabilities: tuple[str, ...]
    technical_actor_ref: str
    human_actor_ref: str | None
    purpose: str
    audience: str
    authorization_context_ref: str
    issued_at: datetime
    deadline: datetime
    scope_refs: tuple[str, ...]
    policy_refs: tuple[str, ...]
    read_only: bool
    page: PageRequest | None = None
    version_token: str | None = None
    idempotency_key: str | None = None

    def __post_init__(self) -> None:
        for field in ("operation_id", "correlation_id", "technical_actor_ref", "purpose", "audience", "authorization_context_ref"):
            object.__setattr__(self, field, text(getattr(self, field), field, InvalidEnvelopeError))
        if not isinstance(self.fcp_version, FCPVersion):
            raise InvalidEnvelopeError("fcp_version must be FCPVersion")
        object.__setattr__(self, "requested_capabilities", string_tuple(self.requested_capabilities, "requested_capabilities", error_type=InvalidEnvelopeError))
        object.__setattr__(self, "scope_refs", string_tuple(self.scope_refs, "scope_refs", allow_empty=False, error_type=InvalidEnvelopeError))
        object.__setattr__(self, "policy_refs", string_tuple(self.policy_refs, "policy_refs", allow_empty=False, error_type=InvalidEnvelopeError))
        object.__setattr__(self, "human_actor_ref", optional_text(self.human_actor_ref, "human_actor_ref", InvalidEnvelopeError))
        object.__setattr__(self, "version_token", optional_text(self.version_token, "version_token", InvalidEnvelopeError))
        object.__setattr__(self, "idempotency_key", optional_text(self.idempotency_key, "idempotency_key", InvalidEnvelopeError))
        issued = instant(self.issued_at, "issued_at", InvalidEnvelopeError)
        deadline = instant(self.deadline, "deadline", InvalidEnvelopeError)
        if deadline <= issued:
            raise InvalidEnvelopeError("deadline must be later than issued_at")
        object.__setattr__(self, "issued_at", issued)
        object.__setattr__(self, "deadline", deadline)
        if type(self.read_only) is not bool or self.read_only is not True:
            raise InvalidEnvelopeError("P-018-01 envelopes must declare read_only=true")
        if self.page is not None and not isinstance(self.page, PageRequest):
            raise InvalidEnvelopeError("page must be PageRequest or null")


@dataclass(frozen=True, slots=True)
class CapabilityProfile:
    supported_versions: tuple[FCPVersion, ...]
    capabilities: tuple[str, ...]
    required_capabilities: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if type(self.supported_versions) not in (tuple, list) or not self.supported_versions:
            raise ValidationError("supported_versions must not be empty")
        if any(not isinstance(item, FCPVersion) for item in self.supported_versions):
            raise ValidationError("supported_versions contains an invalid version")
        versions = tuple(sorted(set(self.supported_versions), reverse=True))
        object.__setattr__(self, "supported_versions", versions)
        capabilities = string_tuple(self.capabilities, "capabilities")
        required = string_tuple(self.required_capabilities, "required_capabilities")
        if not set(required).issubset(capabilities):
            raise ValidationError("required_capabilities must be supported locally")
        object.__setattr__(self, "capabilities", capabilities)
        object.__setattr__(self, "required_capabilities", required)


@dataclass(frozen=True, slots=True)
class NegotiatedProfile:
    version: FCPVersion
    capabilities: tuple[str, ...]
    downgraded: bool


def negotiate(
    local: CapabilityProfile,
    remote: CapabilityProfile,
    *,
    security_critical_capabilities: tuple[str, ...] = (),
    allow_minor_downgrade: bool = True,
) -> NegotiatedProfile:
    """Negotiate a compatible major and capability intersection deterministically."""
    if not isinstance(local, CapabilityProfile) or not isinstance(remote, CapabilityProfile):
        raise ValidationError("local and remote must be CapabilityProfile")
    critical = set(string_tuple(security_critical_capabilities, "security_critical_capabilities"))
    local_majors = {version.major for version in local.supported_versions}
    remote_majors = {version.major for version in remote.supported_versions}
    common_majors = local_majors & remote_majors
    if not common_majors:
        raise UnsupportedVersionError("participants do not share a compatible FCP major")
    major = max(common_majors)
    local_best = max(v for v in local.supported_versions if v.major == major)
    remote_best = max(v for v in remote.supported_versions if v.major == major)
    version = min(local_best, remote_best)
    downgraded = version != local_best or version != remote_best
    if downgraded and not allow_minor_downgrade:
        raise UnsupportedVersionError("minor-version downgrade is not permitted")
    capabilities = tuple(sorted(set(local.capabilities) & set(remote.capabilities)))
    missing = (set(local.required_capabilities) | set(remote.required_capabilities)) - set(capabilities)
    if missing:
        raise CapabilityAbsentError(f"required capability is absent: {', '.join(sorted(missing))}")
    lost_critical = critical & (set(local.capabilities) | set(remote.capabilities)) - set(capabilities)
    if downgraded and lost_critical:
        raise CapabilityAbsentError("downgrade would weaken a security-critical capability")
    return NegotiatedProfile(version, capabilities, downgraded)
