import json
import tempfile
import unittest
from pathlib import Path

from asf.adapters.agent import observe_agent_action
from asf.adapters.dry_run import simulate
from asf.adapters.enforcement_report import report_invariant_ok
from asf.adapters.event import AdapterEvent
from asf.adapters.filesystem import observe_file_write
from asf.adapters.github import observe_repository_action
from asf.adapters.safety import AdapterSafety
from asf.core.invariants import registry as invariant_registry
from asf.runtime import run_loop


ROOT = Path(__file__).resolve().parents[1]


def artifact(name: str) -> str:
    return str(ROOT / "examples" / "artifacts" / name)


def event_fixture(name: str) -> AdapterEvent:
    data = json.loads((ROOT / "examples" / "adapter_events" / name).read_text(encoding="utf-8"))
    return AdapterEvent.from_dict(data)


class AdapterDryRunTests(unittest.TestCase):
    def test_adapter_event_shape(self):
        event = event_fixture("filesystem_write_blocked.json").as_dict()
        for key in [
            "event_id",
            "adapter_name",
            "adapter_mode",
            "observed_action",
            "source_surface",
            "target_surface",
            "artifact_reference",
            "proposed_mutation",
            "actor",
            "timestamp",
            "environment",
            "metadata",
            "event_hash",
        ]:
            self.assertIn(key, event)

    def test_event_hash_stability(self):
        event = event_fixture("filesystem_write_blocked.json")
        self.assertEqual(event.as_dict()["event_hash"], event.as_dict()["event_hash"])

    def test_dry_run_does_not_mutate_filesystem(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "would_not_be_written.txt"
            event = observe_file_write(
                artifact_reference=artifact("release_blocked_missing_tests.json"),
                path=str(target),
                content_preview="do not write",
            )
            report = simulate(event, policy_path=str(ROOT / "policies" / "default.yaml"), root=str(ROOT))
            self.assertFalse(target.exists())
            self.assertFalse(report.mutation_performed)

    def test_filesystem_adapter_emits_event(self):
        event = observe_file_write(
            artifact_reference=artifact("release_blocked_missing_tests.json"),
            path="README.md",
            content_preview="proposed",
        ).as_dict()
        self.assertEqual(event["adapter_name"], "filesystem")
        self.assertEqual(event["proposed_mutation"]["operation"], "write_file")

    def test_github_adapter_dry_run_does_not_call_mutation(self):
        event = observe_repository_action(
            artifact_reference=artifact("release_ready.json"),
            action="release",
            repository="jacksonjp0311-gif/ai-survival-field",
        )
        report = simulate(event, policy_path=str(ROOT / "policies" / "default.yaml"), root=str(ROOT))
        self.assertEqual(event.as_dict()["adapter_name"], "github")
        self.assertFalse(report.mutation_performed)

    def test_agent_adapter_blocks_durable_action(self):
        event = observe_agent_action(
            artifact_reference=artifact("release_ready.json"),
            action="autonomous_action",
        )
        report = simulate(event, policy_path=str(ROOT / "policies" / "default.yaml"), root=str(ROOT))
        self.assertEqual(event.as_dict()["observed_action"], "autonomous_action")
        self.assertEqual(report.enforcement_result, "blocked")
        self.assertIsNotNone(report.wound_id)

    def test_observe_only_produces_no_mutation(self):
        safety = AdapterSafety(mode="observe_only")
        self.assertFalse(safety.can_mutate())

    def test_dry_run_produces_enforcement_report(self):
        report = simulate(event_fixture("filesystem_write_blocked.json"), policy_path=str(ROOT / "policies" / "default.yaml"), root=str(ROOT))
        data = report.as_dict()
        self.assertEqual(data["schema"], "ASF-ENFORCEMENT-REPORT-v0.1")
        self.assertTrue(data["report_id"])

    def test_enforce_full_forbidden_in_v03(self):
        self.assertFalse(AdapterSafety(mode="enforce_full", human_authorized=True).can_mutate())

    def test_enforcement_report_includes_decision_hash(self):
        report = simulate(event_fixture("filesystem_write_blocked.json"), policy_path=str(ROOT / "policies" / "default.yaml"), root=str(ROOT))
        self.assertTrue(report.decision_hash)

    def test_enforcement_report_includes_policy_hash(self):
        report = simulate(event_fixture("filesystem_write_blocked.json"), policy_path=str(ROOT / "policies" / "default.yaml"), root=str(ROOT))
        self.assertTrue(report.policy_hash)

    def test_enforcement_report_includes_event_hash(self):
        event = event_fixture("filesystem_write_blocked.json")
        report = simulate(event, policy_path=str(ROOT / "policies" / "default.yaml"), root=str(ROOT))
        self.assertEqual(report.event_hash, event.as_dict()["event_hash"])

    def test_blocked_adapter_action_emits_wound(self):
        report = simulate(event_fixture("filesystem_write_blocked.json"), policy_path=str(ROOT / "policies" / "default.yaml"), root=str(ROOT))
        self.assertEqual(report.enforcement_result, "blocked")
        self.assertIsNotNone(report.wound_id)

    def test_allowed_draft_dry_run_emits_no_wound(self):
        report = simulate(event_fixture("draft_allowed.json"), policy_path=str(ROOT / "policies" / "default.yaml"), root=str(ROOT))
        self.assertEqual(report.enforcement_result, "dry_run_allowed")
        self.assertIsNone(report.wound_id)

    def test_ui_displays_adapter_mode(self):
        result = run_loop(
            ROOT / "examples" / "artifacts" / "draft_allowed.json",
            action="draft",
            policy_path=ROOT / "policies" / "default.yaml",
            root=ROOT,
            adapter_mode="dry_run",
        )
        self.assertIn("Adapter Mode:   dry_run", result["ui"])

    def test_ledger_records_adapter_event_hash(self):
        event = event_fixture("filesystem_write_blocked.json")
        event_hash = event.as_dict()["event_hash"]
        result = run_loop(
            ROOT / "examples" / "artifacts" / "release_blocked_missing_tests.json",
            action="patch_repository",
            policy_path=ROOT / "policies" / "default.yaml",
            root=ROOT,
            adapter_mode="dry_run",
            adapter_event_hash=event_hash,
        )
        self.assertEqual(result["ledger"]["adapter_event_hash"], event_hash)

    def test_dry_run_success_does_not_close_wound(self):
        report = simulate(event_fixture("filesystem_write_blocked.json"), policy_path=str(ROOT / "policies" / "default.yaml"), root=str(ROOT))
        self.assertEqual(report.enforcement_result, "blocked")
        self.assertFalse(report.mutation_performed)
        self.assertIsNotNone(report.wound_id)

    def test_invariant_check_catches_mutation_performed_true_in_dry_run(self):
        bad = {
            "adapter_mode": "dry_run",
            "mutation_performed": True,
            "event_hash": "event",
            "decision_hash": "decision",
        }
        self.assertFalse(report_invariant_ok(bad))

    def test_v03_invariants_registered(self):
        ids = {item["invariant_id"] for item in invariant_registry()["invariants"]}
        for invariant_id in ["ASF-INV-011", "ASF-INV-012", "ASF-INV-013", "ASF-INV-014", "ASF-INV-015"]:
            self.assertIn(invariant_id, ids)


if __name__ == "__main__":
    unittest.main()
