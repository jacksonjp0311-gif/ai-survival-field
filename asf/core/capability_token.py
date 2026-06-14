from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from asf.core.hashing import stable_hash


@dataclass(frozen=True)
class CapabilityToken:
    schema: str
    token_id: str
    granted_by: str
    granted_to: str
    allowed_action: str
    artifact_hash: str
    policy_hash: str
    adapter: str
    expires_at: str
    scope: dict[str, Any]
    revoked: bool = False

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


def issue_token(
    *,
    granted_by: str,
    granted_to: str,
    allowed_action: str,
    artifact_hash: str,
    policy_hash: str,
    adapter: str = "cli",
    expires_at: str = "2099-01-01T00:00:00+00:00",
    scope: dict[str, Any] | None = None,
) -> CapabilityToken:
    payload = {
        "granted_by": granted_by,
        "granted_to": granted_to,
        "allowed_action": allowed_action,
        "artifact_hash": artifact_hash,
        "policy_hash": policy_hash,
        "adapter": adapter,
        "expires_at": expires_at,
        "scope": scope or {},
    }
    return CapabilityToken(
        schema="ASF-CAPABILITY-TOKEN-v0.1",
        token_id=f"ASF-CAP-{stable_hash(payload)[:12]}",
        scope=scope or {},
        **{key: value for key, value in payload.items() if key != "scope"},
    )


def token_allows(token: CapabilityToken | None, *, action: str, artifact_hash: str, policy_hash: str, adapter: str = "cli") -> bool:
    if token is None or token.revoked:
        return False
    try:
        expires = datetime.fromisoformat(token.expires_at.replace("Z", "+00:00"))
    except ValueError:
        return False
    if expires < datetime.now(timezone.utc):
        return False
    return (
        token.allowed_action == action
        and token.artifact_hash == artifact_hash
        and token.policy_hash == policy_hash
        and token.adapter == adapter
    )

