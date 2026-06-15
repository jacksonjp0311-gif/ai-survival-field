import json
import tempfile
import unittest
from pathlib import Path

from asf.core.invariants import registry as invariant_registry
from asf.repair.repair_dry_run import dry_run
from asf.repair.repair_plan import RepairPlan
from asf.repair.repair_planner import plan_from_wound
from asf.repair.repair_report import build_report
from asf.repair.repair_validation import validate_plan


ROOT = Path(__file__).resolve().parents[1]


def wound() -> dict:
    return json.loads((ROOT / "examples" / "wounds" / "missing_gate_wound.json").read_text(encoding="utf-8"))


def plan() -> RepairPlan:
    return plan_from_wound(
        wound(),
        source_decision_hash="decision-hash",
        source_policy_hash="policy-hash",
        source_ledger_hash="ledger-hash",
    )


class RepairPlannerV05Tests(unittest.TestCase):
    def test_repair_plan_shape(self):
        data = plan().as_dict()
        for key in ["schema", "repair_plan_id", "wound_id", "repair_class", "source_decision_hash", "source_policy_hash", "mutation_mode", "non_claim_lock"]:
            self.assertIn(key, data)

    def test_repair_plan_requires_wound(self):
        with self.assertRaises(ValueError):
            plan_from_wound({}, source_decision_hash="d", source_policy_hash="p")

    def test_repair_plan_is_not_repair(self):
        data = plan().as_dict()
        self.assertFalse(data["repair_performed"])
        self.assertFalse(data["wound_closed"])

    def test_repair_dry_run_no_mutation(self):
        report = dry_run(plan())
        self.assertFalse(report.mutation_performed)
        self.assertFalse(report.repair_performed)

    def test_repair_validation_no_wound_closure(self):
        validation = validate_plan(plan())
        self.assertFalse(validation.wound_closed)

    def test_repair_requires_source_decision_hash(self):
        repair_plan = plan()
        repair_plan.source_decision_hash = ""
        validation = validate_plan(repair_plan)
        self.assertIn("SOURCE_DECISION_HASH_MISSING", validation.failures)

    def test_repair_preserves_policy_hash(self):
        repair_plan = plan()
        self.assertEqual(repair_plan.source_policy_hash, "policy-hash")
        self.assertTrue(validate_plan(repair_plan).valid)

    def test_repair_forbids_self_authorization(self):
        repair_plan = plan()
        repair_plan.authority_granted = True
        self.assertIn("REPAIR_CANNOT_GRANT_AUTHORITY", validate_plan(repair_plan).failures)

    def test_repair_forbids_enforce_full(self):
        repair_plan = plan()
        repair_plan.enforce_full_enabled = True
        self.assertIn("REPAIR_CANNOT_ENABLE_ENFORCE_FULL", validate_plan(repair_plan).failures)

    def test_documentation_alignment_plan(self):
        item = dict(wound())
        item["wound_class"] = "ui_decision_drift"
        item["blocked_reason"] = "UI_DECISION_DRIFT"
        self.assertEqual(plan_from_wound(item, source_decision_hash="d", source_policy_hash="p").repair_class, "documentation_alignment")

    def test_missing_gate_evidence_plan(self):
        self.assertEqual(plan().repair_class, "missing_gate_evidence")

    def test_runtime_geometry_drift_plan(self):
        item = dict(wound())
        item["wound_class"] = "runtime_geometry_drift"
        item["blocked_reason"] = "geometry"
        self.assertEqual(plan_from_wound(item, source_decision_hash="d", source_policy_hash="p").repair_class, "runtime_geometry_drift")

    def test_repository_hygiene_warning_plan(self):
        item = dict(wound())
        item["wound_class"] = "repository_hygiene_warning"
        item["blocked_reason"] = "hygiene warning"
        self.assertEqual(plan_from_wound(item, source_decision_hash="d", source_policy_hash="p").repair_class, "documentation_alignment")

    def test_authorization_missing_plan(self):
        item = dict(wound())
        item["wound_class"] = "authorization_failed"
        item["blocked_reason"] = "ASF007_AUTHORIZATION_FAILED"
        repair_plan = plan_from_wound(item, source_decision_hash="d", source_policy_hash="p")
        self.assertEqual(repair_plan.repair_class, "authorization_missing")
        self.assertIn("request_scoped_authorization", repair_plan.proposed_actions)

    def test_repair_report_shape(self):
        repair_plan = plan()
        dry = dry_run(repair_plan)
        validation = validate_plan(repair_plan)
        data = build_report(repair_plan, dry, validation).as_dict()
        self.assertEqual(data["schema"], "ASF-REPAIR-REPORT-v0.1")
        self.assertTrue(data["repair_report_id"])

    def test_repair_ui_status(self):
        self.assertEqual(dry_run(plan()).ui_status, "repair planned, not repaired")

    def test_repair_ledger_record_hash_available_as_source(self):
        self.assertEqual(plan().source_ledger_hash, "ledger-hash")

    def test_repair_replay_proof_required(self):
        self.assertTrue(validate_plan(plan()).replay_required)

    def test_self_healing_mutation_forbidden(self):
        ids = {item["invariant_id"] for item in invariant_registry()["invariants"]}
        self.assertIn("ASF-INV-030", ids)

    def test_v0_5_release_seal_shape(self):
        seal = json.loads((ROOT / "docs" / "releases" / "ASF-R-v0.5-release-seal.json").read_text(encoding="utf-8"))
        self.assertEqual(seal["schema"], "ASF-RELEASE-SEAL-v0.5")
        self.assertFalse(seal["self_healing_mutation_enabled"])

    def test_repair_dry_run_does_not_write_files(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "repair-output.txt"
            dry_run(plan())
            self.assertFalse(target.exists())

    def test_repair_plan_forbidden_actions_present(self):
        forbidden = set(plan().forbidden_actions)
        self.assertIn("perform_mutation", forbidden)
        self.assertIn("enable_enforce_full", forbidden)

    def test_repair_validation_rejects_forbidden_action(self):
        repair_plan = plan()
        repair_plan.proposed_actions.append("perform_mutation")
        self.assertIn("FORBIDDEN_ACTION_PROPOSED", validate_plan(repair_plan).failures)

    def test_repair_report_does_not_close_wound(self):
        repair_plan = plan()
        report = build_report(repair_plan, dry_run(repair_plan), validate_plan(repair_plan))
        self.assertFalse(report.wound_closed)

    def test_v05_invariants_registered(self):
        ids = {item["invariant_id"] for item in invariant_registry()["invariants"]}
        for invariant_id in ["ASF-INV-021", "ASF-INV-022", "ASF-INV-023", "ASF-INV-024", "ASF-INV-025", "ASF-INV-026", "ASF-INV-027", "ASF-INV-028", "ASF-INV-029", "ASF-INV-030"]:
            self.assertIn(invariant_id, ids)


if __name__ == "__main__":
    unittest.main()
