import json
import unittest
from pathlib import Path

from asf.adapters.safety import AdapterSafety
from asf.core.alignment_auditor import audit_runtime_result
from asf.core.governance_debt import registry as debt_registry
from asf.core.invariants import assert_unknown_not_pass, registry as invariant_registry
from asf.ledger.ledger import verify_record
from asf.ledger.replay import replay_decision
from asf.runtime import run_loop
from asf.ui.doctor import run_doctor


ROOT = Path(__file__).resolve().parents[1]


def release_block_result():
    return run_loop(
        ROOT / "examples" / "artifacts" / "release_blocked_missing_tests.json",
        action="release",
        policy_path=ROOT / "policies" / "default.yaml",
        root=ROOT,
        operator_authorized=True,
    )


def draft_result():
    return run_loop(
        ROOT / "examples" / "artifacts" / "draft_allowed.json",
        action="draft",
        policy_path=ROOT / "policies" / "default.yaml",
        root=ROOT,
        operator_authorized=True,
    )


class EvidenceSealTests(unittest.TestCase):
    def test_invariant_registry_shape(self):
        data = invariant_registry()
        self.assertEqual(data["schema"], "ASF-INVARIANT-REGISTRY-v0.1")
        self.assertGreaterEqual(len(data["invariants"]), 10)

    def test_unknown_is_not_pass(self):
        self.assertFalse(assert_unknown_not_pass("unknown"))
        self.assertFalse(assert_unknown_not_pass(None))
        self.assertTrue(assert_unknown_not_pass("pass"))

    def test_release_block_wound_required_fields(self):
        wound = release_block_result()["wound"]
        for key in ["schema", "wound_id", "wound_class", "subject_artifact", "intended_action", "required_evidence", "non_claim_lock"]:
            self.assertIn(key, wound)

    def test_ledger_required_hashes(self):
        ledger = release_block_result()["ledger"]
        for key in ["decision_hash", "policy_hash", "rhp_state_hash", "rcc_route_hash", "record_hash", "non_claim_lock"]:
            self.assertTrue(ledger[key])

    def test_ledger_verify_accepts_runtime_record(self):
        self.assertTrue(verify_record(release_block_result()["ledger"]))

    def test_ui_matches_blocked_decision(self):
        result = release_block_result()
        self.assertIn("Status:         missing_gate_failed", result["ui"])
        self.assertIn(result["wound"]["wound_id"], result["ui"])

    def test_alignment_auditor_passes_clean_block_result(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        audit = audit_runtime_result(release_block_result(), readme_text=readme)
        self.assertTrue(audit["ok"], audit["failures"])

    def test_alignment_auditor_detects_ui_drift(self):
        result = release_block_result()
        result["ui"] = result["ui"].replace("missing_gate_failed", "pass")
        audit = audit_runtime_result(result)
        self.assertIn("UI_DECISION_DRIFT", audit["failures"])

    def test_replay_passes_same_decision_hash(self):
        result = draft_result()
        report = replay_decision(
            ROOT / "examples" / "artifacts" / "draft_allowed.json",
            action="draft",
            expected_decision_hash=result["decision"]["decision_hash"],
            policy_path=ROOT / "policies" / "default.yaml",
            root=ROOT,
            operator_authorized=True,
        )
        self.assertTrue(report.replay_pass)

    def test_replay_detects_drift(self):
        report = replay_decision(
            ROOT / "examples" / "artifacts" / "draft_allowed.json",
            action="draft",
            expected_decision_hash="not-the-current-hash",
            policy_path=ROOT / "policies" / "default.yaml",
            root=ROOT,
            operator_authorized=True,
        )
        self.assertTrue(report.drift_detected)

    def test_adapter_default_observe_only(self):
        safety = AdapterSafety()
        self.assertEqual(safety.mode, "observe_only")
        self.assertFalse(safety.can_mutate())

    def test_adapter_cannot_self_authorize(self):
        safety = AdapterSafety(mode="enforce_full", self_authorized=True, human_authorized=True)
        self.assertFalse(safety.can_mutate())

    def test_adapter_enforce_full_requires_human_authorization(self):
        safety = AdapterSafety(mode="enforce_full", self_authorized=False, human_authorized=False)
        self.assertFalse(safety.can_mutate())

    def test_adapter_enforce_full_forbidden_before_release_gate(self):
        safety = AdapterSafety(mode="enforce_full", self_authorized=False, human_authorized=True)
        self.assertFalse(safety.can_mutate())

    def test_doctor_passes_clean_repo(self):
        result = run_doctor(ROOT)
        self.assertTrue(result["ok"], result["failures"])

    def test_doctor_detects_missing_root(self):
        result = run_doctor(ROOT / "__missing__")
        self.assertFalse(result["ok"])

    def test_governance_debt_registry_shape(self):
        data = debt_registry()
        self.assertEqual(data["schema"], "ASF-GOVERNANCE-DEBT-REGISTER-v0.1")
        self.assertGreaterEqual(len(data["debts"]), 4)

    def test_release_seal_shape(self):
        seal = json.loads((ROOT / "docs" / "releases" / "ASF-R-v0.1.1-release-seal.json").read_text(encoding="utf-8"))
        self.assertEqual(seal["schema"], "ASF-RELEASE-SEAL-v0.1")
        self.assertEqual(seal["next_version"], "v0.2 Policy-as-Code Hardening")
        self.assertIn("non_claim_lock", seal)

    def test_golden_trace_draft_matches_runtime(self):
        trace = json.loads((ROOT / "examples" / "traces" / "draft_allowed.trace.json").read_text(encoding="utf-8"))
        result = draft_result()
        self.assertEqual(result["decision"]["status"], trace["expected_decision_status"])
        self.assertEqual(result["route"]["target_surface"], trace["expected_route_surface"])

    def test_golden_trace_release_block_matches_runtime(self):
        trace = json.loads((ROOT / "examples" / "traces" / "release_block_missing_tests.trace.json").read_text(encoding="utf-8"))
        result = release_block_result()
        self.assertEqual(result["decision"]["status"], trace["expected_decision_status"])
        self.assertEqual(result["wound"]["wound_class"], trace["expected_wound_class"])


if __name__ == "__main__":
    unittest.main()
