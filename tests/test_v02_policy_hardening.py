import unittest
from pathlib import Path

from asf.core.artifact import ASFArtifact
from asf.core.authorization_receipt import issue_receipt, receipt_allows
from asf.core.capability_token import issue_token, token_allows
from asf.core.hashing import stable_hash
from asf.core.policy import load_policy
from asf.core.policy_diff import diff_policies
from asf.core.validator import validate
from asf.rcc.nexus import orient
from asf.rhp.rehydration import rehydrate
from asf.runtime import run_loop


ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "policies" / "default.yaml"
STRICT = ROOT / "policies" / "strict.json"
LENIENT = ROOT / "policies" / "lenient_release.json"
RELEASE_READY = ROOT / "examples" / "artifacts" / "release_ready.json"


class PolicyHardeningTests(unittest.TestCase):
    def test_policy_hash_bound_in_decision(self):
        result = run_loop(RELEASE_READY, action="release", policy_path=DEFAULT, root=ROOT, operator_authorized=True)
        policy = load_policy(DEFAULT)
        self.assertEqual(result["decision"]["policy_hash"], policy.policy_hash)
        self.assertEqual(result["decision"]["policy_name"], policy.name)

    def test_policy_hash_bound_in_ledger(self):
        result = run_loop(RELEASE_READY, action="release", policy_path=DEFAULT, root=ROOT, operator_authorized=True)
        self.assertEqual(result["ledger"]["policy_hash"], result["decision"]["policy_hash"])

    def test_policy_panel_visible_in_ui(self):
        result = run_loop(RELEASE_READY, action="release", policy_path=DEFAULT, root=ROOT, operator_authorized=True)
        self.assertIn("ACTIVE POLICY", result["ui"])
        self.assertIn("default-asf-policy", result["ui"])

    def test_policy_diff_detects_raised_ceiling(self):
        diff = diff_policies(load_policy(DEFAULT), load_policy(STRICT)).as_dict()
        self.assertIn("release", diff["raised_ceilings"])

    def test_policy_diff_detects_changed_human_authorization(self):
        diff = diff_policies(load_policy(DEFAULT), load_policy(STRICT)).as_dict()
        self.assertIn("publish", diff["changed_human_authorization"])

    def test_policy_diff_detects_lowered_ceiling(self):
        diff = diff_policies(load_policy(DEFAULT), load_policy(LENIENT)).as_dict()
        self.assertIn("release", diff["lowered_ceilings"])

    def test_same_artifact_different_policy_changes_continuation(self):
        default_result = run_loop(RELEASE_READY, action="release", policy_path=DEFAULT, root=ROOT, operator_authorized=True)
        strict_result = run_loop(RELEASE_READY, action="release", policy_path=STRICT, root=ROOT, operator_authorized=True)
        self.assertEqual(default_result["decision"]["status"], "authorization_failed")
        self.assertEqual(strict_result["decision"]["status"], "permission_ceiling_failed")

    def test_dangerous_action_without_capability_token_fails(self):
        artifact = ASFArtifact.load(RELEASE_READY)
        policy = load_policy(DEFAULT)
        decision = validate(artifact, "release", policy, rehydrate(ROOT, operator_authorized=True), orient(artifact, "release"))
        self.assertEqual(decision.status, "authorization_failed")

    def test_capability_token_allows_scoped_action(self):
        artifact = ASFArtifact.load(RELEASE_READY)
        policy = load_policy(DEFAULT)
        artifact_hash = stable_hash(artifact.as_dict())
        token = issue_token(
            granted_by="operator",
            granted_to="cli",
            allowed_action="release",
            artifact_hash=artifact_hash,
            policy_hash=policy.policy_hash,
            adapter="cli",
            scope={"repository": "ai-survival-field", "branch": "main"},
        )
        self.assertTrue(token_allows(token, action="release", artifact_hash=artifact_hash, policy_hash=policy.policy_hash, adapter="cli"))

    def test_capability_token_rejects_wrong_policy_hash(self):
        artifact = ASFArtifact.load(RELEASE_READY)
        policy = load_policy(DEFAULT)
        token = issue_token(
            granted_by="operator",
            granted_to="cli",
            allowed_action="release",
            artifact_hash=stable_hash(artifact.as_dict()),
            policy_hash="wrong",
            adapter="cli",
        )
        self.assertFalse(token_allows(token, action="release", artifact_hash=stable_hash(artifact.as_dict()), policy_hash=policy.policy_hash, adapter="cli"))

    def test_validator_passes_with_valid_capability_token_before_receipt_boundary(self):
        artifact = ASFArtifact.load(RELEASE_READY)
        policy = load_policy(DEFAULT)
        token = issue_token(
            granted_by="operator",
            granted_to="cli",
            allowed_action="release",
            artifact_hash=stable_hash(artifact.as_dict()),
            policy_hash=policy.policy_hash,
            adapter="cli",
        )
        decision = validate(artifact, "release", policy, rehydrate(ROOT, operator_authorized=True), orient(artifact, "release"), capability_token=token)
        self.assertEqual(decision.status, "pass")

    def test_runtime_blocks_valid_token_without_authorization_receipt(self):
        artifact = ASFArtifact.load(RELEASE_READY)
        policy = load_policy(DEFAULT)
        token = issue_token(
            granted_by="operator",
            granted_to="cli",
            allowed_action="release",
            artifact_hash=stable_hash(artifact.as_dict()),
            policy_hash=policy.policy_hash,
            adapter="cli",
        )
        result = run_loop(RELEASE_READY, action="release", policy_path=DEFAULT, root=ROOT, operator_authorized=True, capability_token=token)
        self.assertEqual(result["decision"]["status"], "authorization_failed")

    def test_authorization_receipt_allows_matching_scope(self):
        artifact = ASFArtifact.load(RELEASE_READY)
        policy = load_policy(DEFAULT)
        artifact_hash = stable_hash(artifact.as_dict())
        receipt = issue_receipt(
            operator="James Paul Jackson",
            action="release",
            artifact_hash=artifact_hash,
            policy_hash=policy.policy_hash,
            decision_hash="decision",
            scope={"repository": "ai-survival-field"},
        )
        self.assertTrue(receipt_allows(receipt, action="release", artifact_hash=artifact_hash, policy_hash=policy.policy_hash, decision_hash="decision"))

    def test_authorization_receipt_rejects_wrong_decision_hash(self):
        artifact = ASFArtifact.load(RELEASE_READY)
        policy = load_policy(DEFAULT)
        artifact_hash = stable_hash(artifact.as_dict())
        receipt = issue_receipt(
            operator="James Paul Jackson",
            action="release",
            artifact_hash=artifact_hash,
            policy_hash=policy.policy_hash,
            decision_hash="decision",
        )
        self.assertFalse(receipt_allows(receipt, action="release", artifact_hash=artifact_hash, policy_hash=policy.policy_hash, decision_hash="other"))

    def test_unknown_still_not_pass_under_policy_hardening(self):
        result = run_loop(RELEASE_READY, action="__unknown_action__", policy_path=DEFAULT, root=ROOT, operator_authorized=True)
        self.assertNotEqual(result["decision"]["status"], "pass")

    def test_no_adapter_mutation_enabled_by_policy_work(self):
        from asf.adapters.safety import AdapterSafety

        self.assertFalse(AdapterSafety(mode="observe_only", human_authorized=True).can_mutate())
        self.assertFalse(AdapterSafety(mode="dry_run", human_authorized=True).can_mutate())

    def test_policy_hash_changes_when_policy_changes(self):
        self.assertNotEqual(load_policy(DEFAULT).policy_hash, load_policy(STRICT).policy_hash)


if __name__ == "__main__":
    unittest.main()

