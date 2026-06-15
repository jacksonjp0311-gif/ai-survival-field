import json
import tempfile
import unittest
from pathlib import Path

from asf.core.invariants import registry as invariant_registry
from asf.repair.bounded_executor import execute_bounded
from asf.repair.repair_authorization import build_receipt
from asf.repair.repair_plan import RepairPlan
from asf.wounds.closure import build_closure_request, close_wound, validate_closure


ROOT = Path(__file__).resolve().parents[1]


def doc_plan() -> RepairPlan:
    data = json.loads((ROOT / "examples" / "repair_plans" / "documentation_alignment_repair_plan.json").read_text(encoding="utf-8"))
    return RepairPlan.from_dict(data)


def execution_report() -> dict:
    with tempfile.TemporaryDirectory() as temp:
        plan = doc_plan()
        result = execute_bounded(plan, build_receipt(plan, human_authorizer="James", allowed_paths=["docs"]), root=temp, target_path="docs/a.md")
        return result.as_dict()


class ControlledWoundClosureTests(unittest.TestCase):
    def test_closure_request_shape(self):
        request = build_closure_request(execution_report(), wound_id="ASF-WOUND-doc-alignment", closure_authorizer="James")
        data = request.as_dict()
        for key in ["schema", "wound_id", "repair_plan_hash", "repair_replay_hash", "repair_execution_hash", "post_repair_hash", "closure_authorizer"]:
            self.assertIn(key, data)

    def test_closure_validation_passes_exact_evidence(self):
        execution = execution_report()
        request = build_closure_request(execution, wound_id="ASF-WOUND-doc-alignment", closure_authorizer="James")
        self.assertTrue(validate_closure(request, execution).valid)

    def test_closure_validation_fails_missing_wound_id(self):
        execution = execution_report()
        request = build_closure_request(execution, wound_id="", closure_authorizer="James")
        self.assertIn("WOUND_ID_MISSING", validate_closure(request, execution).failures)

    def test_closure_validation_fails_missing_authorizer(self):
        execution = execution_report()
        request = build_closure_request(execution, wound_id="ASF-WOUND-doc-alignment", closure_authorizer="")
        self.assertIn("CLOSURE_AUTHORIZER_MISSING", validate_closure(request, execution).failures)

    def test_closure_validation_fails_post_repair_hash_drift(self):
        execution = execution_report()
        request = build_closure_request(execution, wound_id="ASF-WOUND-doc-alignment", closure_authorizer="James")
        request.post_repair_hash = "wrong"
        self.assertIn("POST_REPAIR_HASH_MISMATCH", validate_closure(request, execution).failures)

    def test_closure_validation_fails_repair_execution_hash_drift(self):
        execution = execution_report()
        request = build_closure_request(execution, wound_id="ASF-WOUND-doc-alignment", closure_authorizer="James")
        request.repair_execution_hash = "wrong"
        self.assertIn("REPAIR_EXECUTION_HASH_MISMATCH", validate_closure(request, execution).failures)

    def test_closure_validation_fails_authorization_hash_drift(self):
        execution = execution_report()
        request = build_closure_request(execution, wound_id="ASF-WOUND-doc-alignment", closure_authorizer="James")
        request.authorization_receipt_hash = "wrong"
        self.assertIn("AUTHORIZATION_RECEIPT_HASH_MISMATCH", validate_closure(request, execution).failures)

    def test_closure_validation_fails_when_execution_not_applied(self):
        execution = execution_report()
        execution["status"] = "blocked"
        request = build_closure_request(execution, wound_id="ASF-WOUND-doc-alignment", closure_authorizer="James")
        self.assertIn("REPAIR_EXECUTION_NOT_APPLIED", validate_closure(request, execution).failures)

    def test_closure_validation_fails_if_execution_already_closed(self):
        execution = execution_report()
        execution["wound_closed"] = True
        request = build_closure_request(execution, wound_id="ASF-WOUND-doc-alignment", closure_authorizer="James")
        self.assertIn("WOUND_ALREADY_CLOSED", validate_closure(request, execution).failures)

    def test_closure_record_shape(self):
        execution = execution_report()
        request = build_closure_request(execution, wound_id="ASF-WOUND-doc-alignment", closure_authorizer="James")
        record = close_wound(request, execution).as_dict()
        self.assertEqual(record["schema"], "ASF-WOUND-CLOSURE-RECORD-v0.1")
        self.assertTrue(record["closure_record_id"])

    def test_closure_record_closes_wound(self):
        execution = execution_report()
        request = build_closure_request(execution, wound_id="ASF-WOUND-doc-alignment", closure_authorizer="James")
        self.assertTrue(close_wound(request, execution).wound_closed)

    def test_closure_record_performs_no_repair_mutation(self):
        execution = execution_report()
        request = build_closure_request(execution, wound_id="ASF-WOUND-doc-alignment", closure_authorizer="James")
        self.assertFalse(close_wound(request, execution).mutation_performed)

    def test_closure_record_grants_no_authority(self):
        execution = execution_report()
        request = build_closure_request(execution, wound_id="ASF-WOUND-doc-alignment", closure_authorizer="James")
        self.assertFalse(close_wound(request, execution).authority_granted)

    def test_close_wound_raises_on_invalid_request(self):
        execution = execution_report()
        request = build_closure_request(execution, wound_id="", closure_authorizer="James")
        with self.assertRaises(ValueError):
            close_wound(request, execution)

    def test_closure_non_claim_lock(self):
        execution = execution_report()
        request = build_closure_request(execution, wound_id="ASF-WOUND-doc-alignment", closure_authorizer="James")
        self.assertIn("no general authority", close_wound(request, execution).non_claim_lock)

    def test_closure_validation_is_not_general_healing_claim(self):
        execution = execution_report()
        request = build_closure_request(execution, wound_id="ASF-WOUND-doc-alignment", closure_authorizer="James")
        self.assertIn("not a general healing claim", validate_closure(request, execution).non_claim_lock)

    def test_v08_invariants_registered(self):
        ids = {item["invariant_id"] for item in invariant_registry()["invariants"]}
        for invariant_id in ["ASF-INV-049", "ASF-INV-050", "ASF-INV-051", "ASF-INV-052", "ASF-INV-053", "ASF-INV-054", "ASF-INV-055"]:
            self.assertIn(invariant_id, ids)

    def test_v08_release_seal_exists(self):
        seal = json.loads((ROOT / "docs" / "releases" / "ASF-R-v0.8-release-seal.json").read_text(encoding="utf-8"))
        self.assertEqual(seal["schema"], "ASF-RELEASE-SEAL-v0.8")
        self.assertFalse(seal["self_healing_mutation_enabled"])

    def test_repaired_wound_is_not_closed_before_closure_record(self):
        execution = execution_report()
        self.assertTrue(execution["repair_performed"])
        self.assertFalse(execution["wound_closed"])

    def test_closure_requires_exact_scope(self):
        execution = execution_report()
        request = build_closure_request(execution, wound_id="ASF-WOUND-doc-alignment", closure_authorizer="James")
        request.closure_scope = "all_wounds"
        self.assertIn("CLOSURE_SCOPE_NOT_EXACT", validate_closure(request, execution).failures)

    def test_closure_request_is_not_closure(self):
        request = build_closure_request(execution_report(), wound_id="ASF-WOUND-doc-alignment", closure_authorizer="James")
        self.assertIn("not wound closure", request.non_claim_lock)

    def test_closure_validation_fails_repair_plan_hash_drift(self):
        execution = execution_report()
        request = build_closure_request(execution, wound_id="ASF-WOUND-doc-alignment", closure_authorizer="James")
        request.repair_plan_hash = "wrong"
        self.assertIn("REPAIR_PLAN_HASH_MISMATCH", validate_closure(request, execution).failures)

    def test_closure_validation_fails_replay_hash_drift(self):
        execution = execution_report()
        request = build_closure_request(execution, wound_id="ASF-WOUND-doc-alignment", closure_authorizer="James")
        request.repair_replay_hash = "wrong"
        self.assertIn("REPAIR_REPLAY_HASH_MISMATCH", validate_closure(request, execution).failures)

    def test_closure_record_binds_authorizer(self):
        execution = execution_report()
        request = build_closure_request(execution, wound_id="ASF-WOUND-doc-alignment", closure_authorizer="James")
        self.assertEqual(close_wound(request, execution).closure_authorizer, "James")


if __name__ == "__main__":
    unittest.main()
