import json
import unittest
from pathlib import Path

from asf.core.hashing import stable_hash
from asf.core.invariants import registry as invariant_registry
from asf.core.latest_pointer import load_latest_pointer, validate_latest_pointer
from asf.repair.repair_plan import RepairPlan
from asf.repair.repair_replay import replay_repair


ROOT = Path(__file__).resolve().parents[1]
REMOTE_HEAD = "ed6468ec63d376e343e41d5989688c756aefd3c7"


def plan() -> RepairPlan:
    data = json.loads((ROOT / "examples" / "repair_plans" / "missing_gate_repair_plan.json").read_text(encoding="utf-8"))
    return RepairPlan.from_dict(data)


class RepairReplayV06Tests(unittest.TestCase):
    def test_repair_replay_shape(self):
        report = replay_repair(plan()).as_dict()
        for key in ["schema", "replay_id", "repair_plan_hash", "dry_run_hash", "validation_hash", "replay_pass", "non_claim_lock"]:
            self.assertIn(key, report)

    def test_repair_replay_passes_valid_plan(self):
        self.assertTrue(replay_repair(plan()).replay_pass)

    def test_repair_replay_does_not_mutate(self):
        report = replay_repair(plan())
        self.assertFalse(report.mutation_performed)
        self.assertFalse(report.repair_performed)

    def test_repair_replay_does_not_close_wound(self):
        self.assertFalse(replay_repair(plan()).wound_closed)

    def test_repair_replay_does_not_grant_authority(self):
        self.assertFalse(replay_repair(plan()).authority_granted)

    def test_repair_replay_detects_plan_hash_drift(self):
        report = replay_repair(plan(), expected_repair_plan_hash="wrong")
        self.assertFalse(report.replay_pass)
        self.assertTrue(report.drift_detected)
        self.assertIn("REPAIR_PLAN_HASH_DRIFT", report.failures)

    def test_repair_replay_accepts_expected_hash(self):
        repair_plan = plan()
        expected = stable_hash(repair_plan.as_dict())
        self.assertTrue(replay_repair(repair_plan, expected_repair_plan_hash=expected).replay_pass)

    def test_repair_replay_rejects_missing_decision_hash(self):
        repair_plan = plan()
        repair_plan.source_decision_hash = ""
        report = replay_repair(repair_plan)
        self.assertFalse(report.replay_pass)
        self.assertIn("SOURCE_DECISION_HASH_MISSING", report.failures)

    def test_latest_pointer_not_pending(self):
        pointer = load_latest_pointer(ROOT / "docs" / "context" / "latest-asf.json")
        self.assertNotEqual(pointer["latest_commit"], "pending")

    def test_latest_pointer_alignment_passes_observed_commit(self):
        pointer = load_latest_pointer(ROOT / "docs" / "context" / "latest-asf.json")
        result = validate_latest_pointer(pointer, observed_commit=REMOTE_HEAD)
        self.assertTrue(result["ok"], result["failures"])

    def test_latest_pointer_alignment_detects_pending(self):
        pointer = load_latest_pointer(ROOT / "docs" / "context" / "latest-asf.json")
        pointer["latest_commit"] = "pending"
        result = validate_latest_pointer(pointer, observed_commit=REMOTE_HEAD)
        self.assertFalse(result["ok"])
        self.assertIn("LATEST_COMMIT_PENDING", result["failures"])

    def test_latest_pointer_alignment_detects_drift(self):
        pointer = load_latest_pointer(ROOT / "docs" / "context" / "latest-asf.json")
        result = validate_latest_pointer(pointer, observed_commit="different")
        self.assertFalse(result["ok"])
        self.assertIn("LATEST_COMMIT_DRIFT", result["failures"])

    def test_v06_invariants_registered(self):
        ids = {item["invariant_id"] for item in invariant_registry()["invariants"]}
        for invariant_id in ["ASF-INV-031", "ASF-INV-032", "ASF-INV-033", "ASF-INV-034", "ASF-INV-035"]:
            self.assertIn(invariant_id, ids)

    def test_v06_release_seal_shape(self):
        seal = json.loads((ROOT / "docs" / "releases" / "ASF-R-v0.6-release-seal.json").read_text(encoding="utf-8"))
        self.assertEqual(seal["schema"], "ASF-RELEASE-SEAL-v0.6")
        self.assertFalse(seal["wound_closure_enabled"])

    def test_repair_replay_cli_non_claim_lock_text(self):
        report = replay_repair(plan()).as_dict()
        self.assertIn("not wound closure", report["non_claim_lock"])


if __name__ == "__main__":
    unittest.main()
