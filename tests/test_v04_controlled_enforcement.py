import json
import tempfile
import unittest
from pathlib import Path

from asf.adapters.agent import observe_agent_action
from asf.adapters.block_enforcer import enforce_block_only, event_for_artifact
from asf.adapters.event import AdapterEvent
from asf.adapters.filesystem import observe_file_write
from asf.adapters.github import observe_repository_action
from asf.adapters.safety import AdapterSafety
from asf.core.invariants import registry as invariant_registry


ROOT = Path(__file__).resolve().parents[1]


def artifact(name: str) -> str:
    return str(ROOT / "examples" / "artifacts" / name)


def event_fixture(name: str) -> AdapterEvent:
    data = json.loads((ROOT / "examples" / "adapter_events" / name).read_text(encoding="utf-8"))
    return AdapterEvent.from_dict(data)


class ControlledEnforcementTests(unittest.TestCase):
    def test_enforce_block_only_blocks_unsafe_release(self):
        result = enforce_block_only(
            event_for_artifact(artifact("release_blocked_missing_tests.json"), "release"),
            policy_path=str(ROOT / "policies" / "default.yaml"),
            root=str(ROOT),
        )
        self.assertEqual(result.decision["status"], "missing_gate_failed")
        self.assertEqual(result.exit_code, 2)

    def test_enforce_block_only_permits_bounded_draft(self):
        result = enforce_block_only(
            event_for_artifact(artifact("draft_allowed.json"), "draft"),
            policy_path=str(ROOT / "policies" / "default.yaml"),
            root=str(ROOT),
        )
        self.assertEqual(result.decision["status"], "pass")
        self.assertEqual(result.exit_code, 0)

    def test_blocked_enforcement_returns_nonzero(self):
        result = enforce_block_only(
            event_fixture("filesystem_write_blocked.json"),
            policy_path=str(ROOT / "policies" / "default.yaml"),
            root=str(ROOT),
        )
        self.assertEqual(result.exit_code, 2)

    def test_permitted_enforcement_returns_zero(self):
        result = enforce_block_only(
            event_fixture("draft_allowed.json"),
            policy_path=str(ROOT / "policies" / "default.yaml"),
            root=str(ROOT),
        )
        self.assertEqual(result.exit_code, 0)

    def test_blocked_enforcement_emits_wound(self):
        result = enforce_block_only(
            event_fixture("filesystem_write_blocked.json"),
            policy_path=str(ROOT / "policies" / "default.yaml"),
            root=str(ROOT),
        )
        self.assertIsNotNone(result.wound)
        self.assertTrue(result.wound["wound_id"])

    def test_blocked_enforcement_emits_ledger(self):
        result = enforce_block_only(
            event_fixture("filesystem_write_blocked.json"),
            policy_path=str(ROOT / "policies" / "default.yaml"),
            root=str(ROOT),
        )
        self.assertTrue(result.ledger["record_hash"])
        self.assertTrue(result.ledger["adapter_event_hash"])

    def test_blocked_enforcement_emits_enforcement_report(self):
        result = enforce_block_only(
            event_fixture("filesystem_write_blocked.json"),
            policy_path=str(ROOT / "policies" / "default.yaml"),
            root=str(ROOT),
        )
        self.assertEqual(result.enforcement_report["schema"], "ASF-ENFORCEMENT-REPORT-v0.1")
        self.assertEqual(result.enforcement_report["enforcement_result"], "block_enforced")

    def test_blocked_enforcement_renders_ui_status(self):
        result = enforce_block_only(
            event_fixture("filesystem_write_blocked.json"),
            policy_path=str(ROOT / "policies" / "default.yaml"),
            root=str(ROOT),
        )
        self.assertIn("Adapter Mode:   enforce_block_only", result.ui)
        self.assertIn("Status:         permission_ceiling_failed", result.ui)

    def test_enforce_block_only_does_not_mutate_filesystem(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "must_not_exist.txt"
            event = observe_file_write(
                artifact_reference=artifact("release_blocked_missing_tests.json"),
                path=str(target),
                content_preview="blocked content",
                mode="enforce_block_only",
            )
            result = enforce_block_only(event, policy_path=str(ROOT / "policies" / "default.yaml"), root=str(ROOT))
            self.assertEqual(result.exit_code, 2)
            self.assertFalse(target.exists())
            self.assertFalse(result.mutation_performed)

    def test_enforce_block_only_does_not_call_github_mutation(self):
        event = observe_repository_action(
            artifact_reference=artifact("release_ready.json"),
            action="release",
            repository="jacksonjp0311-gif/ai-survival-field",
            mode="enforce_block_only",
        )
        result = enforce_block_only(event, policy_path=str(ROOT / "policies" / "default.yaml"), root=str(ROOT))
        self.assertEqual(event.as_dict()["adapter_name"], "github")
        self.assertFalse(result.mutation_performed)

    def test_enforce_block_only_does_not_update_memory(self):
        event = observe_agent_action(
            artifact_reference=artifact("release_ready.json"),
            action="update_memory",
            mode="enforce_block_only",
        )
        result = enforce_block_only(event, policy_path=str(ROOT / "policies" / "default.yaml"), root=str(ROOT))
        self.assertEqual(event.as_dict()["observed_action"], "update_memory")
        self.assertFalse(result.mutation_performed)

    def test_enforce_full_remains_forbidden(self):
        self.assertFalse(AdapterSafety(mode="enforce_full", human_authorized=True).can_mutate())

    def test_controlled_block_does_not_close_wound(self):
        result = enforce_block_only(
            event_fixture("filesystem_write_blocked.json"),
            policy_path=str(ROOT / "policies" / "default.yaml"),
            root=str(ROOT),
        )
        self.assertFalse(result.wound_closed)
        self.assertIsNotNone(result.wound)

    def test_controlled_block_does_not_count_as_repair(self):
        result = enforce_block_only(
            event_fixture("filesystem_write_blocked.json"),
            policy_path=str(ROOT / "policies" / "default.yaml"),
            root=str(ROOT),
        )
        self.assertFalse(result.repair_performed)

    def test_github_actions_template_exists(self):
        self.assertTrue((ROOT / ".github" / "workflows" / "asf-guard.yml").is_file())

    def test_workflow_template_contains_no_mutation_step(self):
        text = (ROOT / ".github" / "workflows" / "asf-guard.yml").read_text(encoding="utf-8").lower()
        forbidden = ["git push", "gh release", "gh api", "pypi", "twine upload"]
        for token in forbidden:
            self.assertNotIn(token, text)

    def test_release_seal_records_controlled_enforcement_boundary(self):
        seal = json.loads((ROOT / "docs" / "releases" / "ASF-R-v0.4-release-seal.json").read_text(encoding="utf-8"))
        self.assertEqual(seal["version"], "v0.4")
        self.assertIn("controlled block enforcement", seal["non_claim_lock"])
        self.assertEqual(seal["next_version"], "v0.5 Repair Planner Dry Run")

    def test_v04_invariants_registered(self):
        ids = {item["invariant_id"] for item in invariant_registry()["invariants"]}
        for invariant_id in ["ASF-INV-016", "ASF-INV-017", "ASF-INV-018", "ASF-INV-019", "ASF-INV-020"]:
            self.assertIn(invariant_id, ids)


if __name__ == "__main__":
    unittest.main()
