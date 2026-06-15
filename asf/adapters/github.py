from __future__ import annotations

from asf.adapters.event import AdapterEvent


GITHUB_ACTIONS = {"patch_repository", "commit", "release", "publish", "mark_canonical"}


def observe_repository_action(*, artifact_reference: str, action: str, repository: str, actor: str = "operator", mode: str = "dry_run") -> AdapterEvent:
    if action not in GITHUB_ACTIONS:
        action = "patch_repository"
    return AdapterEvent(
        adapter_name="github",
        adapter_mode=mode,
        observed_action=action,
        source_surface="github",
        target_surface="repository",
        artifact_reference=artifact_reference,
        proposed_mutation={"operation": action, "repository": repository},
        actor=actor,
    )

