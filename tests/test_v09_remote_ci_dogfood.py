import json
import unittest
from pathlib import Path

from asf.ci.evidence import build_ci_evidence, summarize_ci_for_pointer, verify_ci_evidence
from asf.core.invariants import registry as invariant_registry
from asf.demo import public_demo
from asf.dogfood import run_dogfood


ROOT = Path(__file__).resolve().parents[1]


class RemoteCIDogfoodTests(unittest.TestCase):
    def test_ci_evidence_shape(self):
        evidence = build_ci_evidence(commit="abc", test_count=180).as_dict()
        for key in ["schema", "commit", "workflow_name", "status", "test_count", "source", "mutation_performed", "evidence_hash"]:
            self.assertIn(key, evidence)

    def test_ci_evidence_verifies(self):
        evidence = build_ci_evidence(commit="abc", test_count=180).as_dict()
        self.assertTrue(verify_ci_evidence(evidence)["ok"])

    def test_ci_evidence_rejects_mutation(self):
        evidence = build_ci_evidence(commit="abc", test_count=180).as_dict()
        evidence["mutation_performed"] = True
        self.assertIn("CI_MUTATION_NOT_ALLOWED", verify_ci_evidence(evidence)["failures"])

    def test_ci_evidence_rejects_missing_commit(self):
        evidence = build_ci_evidence(commit="", test_count=180).as_dict()
        self.assertIn("CI_COMMIT_MISSING", verify_ci_evidence(evidence)["failures"])

    def test_ci_evidence_rejects_bad_status(self):
        evidence = build_ci_evidence(commit="abc", test_count=180).as_dict()
        evidence["status"] = "greenish"
        self.assertIn("CI_STATUS_INVALID", verify_ci_evidence(evidence)["failures"])

    def test_ci_summary_marks_github_actions_verified(self):
        evidence = build_ci_evidence(commit="abc", test_count=180, status="remote_pass", source="github_actions").as_dict()
        self.assertTrue(summarize_ci_for_pointer(evidence)["remote_ci_verified"])

    def test_ci_summary_does_not_mark_local_verified(self):
        evidence = build_ci_evidence(commit="abc", test_count=180, status="local_pass", source="local").as_dict()
        self.assertFalse(summarize_ci_for_pointer(evidence)["remote_ci_verified"])

    def test_dogfood_report_shape(self):
        report = run_dogfood(ROOT)
        self.assertEqual(report["schema"], "ASF-DOGFOOD-REPORT-v0.1")
        self.assertTrue(report["dogfood_hash"])

    def test_dogfood_report_passes_core_loop(self):
        report = run_dogfood(ROOT)
        self.assertEqual(report["draft_status"], "pass")
        self.assertIn(report["blocked_release_status"], {"missing_gate_failed", "permission_ceiling_failed"})
        self.assertTrue(report["repair_replay_pass"])
        self.assertTrue(report["closure_validation_pass"])

    def test_dogfood_report_non_mutating(self):
        self.assertFalse(run_dogfood(ROOT)["mutation_performed"])

    def test_public_demo_shape(self):
        demo = public_demo(ROOT)
        self.assertEqual(demo["schema"], "ASF-PUBLIC-DEMO-v0.1")
        self.assertIn("evidence-gated recovery", demo["headline"])

    def test_public_demo_non_mutating(self):
        self.assertFalse(public_demo(ROOT)["mutation_performed"])

    def test_public_demo_contains_recovery_loop(self):
        loop = public_demo(ROOT)["loop"]
        self.assertIn("detect wound", loop)
        self.assertIn("validate closure", loop)

    def test_workflow_uploads_ci_evidence_artifact(self):
        workflow = (ROOT / ".github" / "workflows" / "asf-guard.yml").read_text(encoding="utf-8")
        self.assertIn("actions/upload-artifact", workflow)
        self.assertIn("asf-ci-evidence.json", workflow)

    def test_workflow_runs_dogfood_and_demo(self):
        workflow = (ROOT / ".github" / "workflows" / "asf-guard.yml").read_text(encoding="utf-8")
        self.assertIn("python -m asf.cli dogfood run", workflow)
        self.assertIn("python -m asf.cli demo", workflow)

    def test_workflow_has_read_only_permissions(self):
        workflow = (ROOT / ".github" / "workflows" / "asf-guard.yml").read_text(encoding="utf-8")
        self.assertIn("contents: read", workflow)

    def test_workflow_contains_no_mutation_commands(self):
        workflow = (ROOT / ".github" / "workflows" / "asf-guard.yml").read_text(encoding="utf-8").lower()
        for token in ["git push", "gh release", "twine upload", "gh api"]:
            self.assertNotIn(token, workflow)

    def test_v09_release_seal_exists(self):
        seal = json.loads((ROOT / "docs" / "releases" / "ASF-R-v0.9-release-seal.json").read_text(encoding="utf-8"))
        self.assertEqual(seal["schema"], "ASF-RELEASE-SEAL-v0.9")
        self.assertTrue(seal["dogfood_enabled"])

    def test_v09_invariants_registered(self):
        ids = {item["invariant_id"] for item in invariant_registry()["invariants"]}
        for invariant_id in ["ASF-INV-056", "ASF-INV-057", "ASF-INV-058", "ASF-INV-059", "ASF-INV-060"]:
            self.assertIn(invariant_id, ids)

    def test_remote_ci_doc_states_non_claim_lock(self):
        text = (ROOT / "docs" / "remote_ci_evidence.md").read_text(encoding="utf-8")
        self.assertIn("not production safety", text)


if __name__ == "__main__":
    unittest.main()
