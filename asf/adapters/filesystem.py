from __future__ import annotations

from asf.adapters.event import AdapterEvent


def observe_file_write(*, artifact_reference: str, path: str, content_preview: str, actor: str = "operator", mode: str = "dry_run") -> AdapterEvent:
    return AdapterEvent(
        adapter_name="filesystem",
        adapter_mode=mode,
        observed_action="patch_repository",
        source_surface="filesystem",
        target_surface="repository",
        artifact_reference=artifact_reference,
        proposed_mutation={"operation": "write_file", "path": path, "content_preview": content_preview},
        actor=actor,
    )


def observe_file_delete(*, artifact_reference: str, path: str, actor: str = "operator", mode: str = "dry_run") -> AdapterEvent:
    return AdapterEvent(
        adapter_name="filesystem",
        adapter_mode=mode,
        observed_action="patch_repository",
        source_surface="filesystem",
        target_surface="repository",
        artifact_reference=artifact_reference,
        proposed_mutation={"operation": "delete_file", "path": path},
        actor=actor,
    )

