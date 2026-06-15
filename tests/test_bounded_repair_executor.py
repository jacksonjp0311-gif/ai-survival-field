import json
import tempfile
import unittest
from pathlib import Path

from asf.adapters.safety import AdapterSafety
from asf.core.invariants import registry as invariant_registry
from asf.repair.bounded_executor import execute_bounded
from asf.repair.repair_authorization import build_receipt
from asf.repair.repair_plan import RepairPlan


ROOT = Path(__file__).resolve().parents[1]


def load_plan(name: str = "documentation_alignment_repair_plan.json") -> RepairPlan:
    return RepairPlan.from_dict(json.loads((ROOT / "examples" / "repair_plans" / name).read_text(encoding="utf-8")))


def receipt_for(plan: RepairPlan, paths: list[str] | None = None):
    return build_receipt(plan, human_authorizer="James", allowed_paths=paths or ["docs"])


class BoundedRepairExecutorTests(unittest.TestCase):
    def test_bounded_executor_refuses_missing_authorization(self):
        result = execute_bounded(load_plan(), None, root=tempfile.mkdtemp(), target_path="docs/a.md")
        self.assertEqual(result.status, "blocked")
        self.assertIn("AUTHORIZATION_RECEIPT_MISSING", result.failures)

    def test_bounded_executor_refuses_non_replayed_plan(self):
        plan = load_plan()
        plan.source_decision_hash = ""
        result = execute_bounded(plan, receipt_for(load_plan()), root=tempfile.mkdtemp(), target_path="docs/a.md")
        self.assertIn("REPAIR_REPLAY_NOT_PASS", result.failures)

    def test_bounded_executor_refuses_policy_mutation(self):
        plan = load_plan()
        result = execute_bounded(plan, receipt_for(plan, ["policies"]), root=tempfile.mkdtemp(), target_path="policies/default.yaml")
        self.assertIn("FORBIDDEN_PATH", result.failures)

    def test_bounded_executor_refuses_validator_mutation(self):
        plan = load_plan()
        result = execute_bounded(plan, receipt_for(plan, ["asf/core"]), root=tempfile.mkdtemp(), target_path="asf/core/validator.py")
        self.assertIn("FORBIDDEN_PATH", result.failures)

    def test_bounded_executor_refuses_adapter_enforcement_mutation(self):
        plan = load_plan()
        result = execute_bounded(plan, receipt_for(plan, ["asf/adapters"]), root=tempfile.mkdtemp(), target_path="asf/adapters/safety.py")
        self.assertIn("FORBIDDEN_PATH", result.failures)

    def test_bounded_executor_refuses_memory_mutation(self):
        plan = load_plan()
        result = execute_bounded(plan, receipt_for(plan, ["memory"]), root=tempfile.mkdtemp(), target_path="memory/state.json")
        self.assertIn("FORBIDDEN_PATH", result.failures)

    def test_bounded_executor_allows_documentation_alignment_with_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            plan = load_plan()
            result = execute_bounded(plan, receipt_for(plan), root=temp, target_path="docs/a.md", content="aligned\n")
            self.assertEqual(result.status, "applied", result.failures)
            self.assertTrue((Path(temp) / "docs" / "a.md").is_file())

    def test_bounded_executor_emits_pre_post_hashes(self):
        with tempfile.TemporaryDirectory() as temp:
            plan = load_plan()
            result = execute_bounded(plan, receipt_for(plan), root=temp, target_path="docs/a.md")
            evidence = result.evidence
            self.assertTrue(evidence["pre_repair_hash"])
            self.assertTrue(evidence["post_repair_hash"])

    def test_bounded_executor_emits_diff_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            plan = load_plan()
            result = execute_bounded(plan, receipt_for(plan), root=temp, target_path="docs/a.md")
            self.assertTrue(result.evidence["proposed_diff_hash"])

    def test_bounded_executor_writes_ledger_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            plan = load_plan()
            result = execute_bounded(plan, receipt_for(plan), root=temp, target_path="docs/a.md")
            self.assertTrue(result.ledger_evidence_hash)

    def test_bounded_executor_leaves_wound_closed_false(self):
        with tempfile.TemporaryDirectory() as temp:
            plan = load_plan()
            result = execute_bounded(plan, receipt_for(plan), root=temp, target_path="docs/a.md")
            self.assertFalse(result.wound_closed)
            self.assertFalse(result.evidence["wound_closed"])

    def test_bounded_repair_is_not_self_healing_mutation(self):
        with tempfile.TemporaryDirectory() as temp:
            plan = load_plan()
            result = execute_bounded(plan, receipt_for(plan), root=temp, target_path="docs/a.md")
            self.assertFalse(result.authority_granted)
            self.assertIn("Authorization permits only one bounded local repair plan", result.non_claim_lock)

    def test_enforce_full_remains_forbidden(self):
        self.assertFalse(AdapterSafety(mode="enforce_full", human_authorized=True).can_mutate())

    def test_v07_release_seal_exists(self):
        seal = json.loads((ROOT / "docs" / "releases" / "ASF-R-v0.7-release-seal.json").read_text(encoding="utf-8"))
        self.assertEqual(seal["schema"], "ASF-RELEASE-SEAL-v0.7")
        self.assertFalse(seal["wound_closure_enabled"])

    def test_executor_refuses_non_allowlisted_repair_class(self):
        plan = load_plan("missing_gate_repair_plan.json")
        result = execute_bounded(plan, receipt_for(plan), root=tempfile.mkdtemp(), target_path="docs/a.md")
        self.assertIn("REPAIR_CLASS_NOT_ALLOWLISTED", result.failures)

    def test_executor_emits_authorization_receipt_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            plan = load_plan()
            result = execute_bounded(plan, receipt_for(plan), root=temp, target_path="docs/a.md")
            self.assertTrue(result.authorization_receipt_hash)

    def test_executor_refuses_release_path(self):
        plan = load_plan()
        result = execute_bounded(plan, receipt_for(plan, ["releases"]), root=tempfile.mkdtemp(), target_path="releases/v1.json")
        self.assertIn("FORBIDDEN_PATH", result.failures)

    def test_v07_invariants_registered(self):
        ids = {item["invariant_id"] for item in invariant_registry()["invariants"]}
        for invariant_id in ["ASF-INV-041", "ASF-INV-042", "ASF-INV-043", "ASF-INV-044", "ASF-INV-045", "ASF-INV-046", "ASF-INV-047", "ASF-INV-048"]:
            self.assertIn(invariant_id, ids)


if __name__ == "__main__":
    unittest.main()
