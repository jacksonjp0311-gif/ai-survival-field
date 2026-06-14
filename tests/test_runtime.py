import unittest
from pathlib import Path

from asf.runtime import run_loop


ROOT = Path(__file__).resolve().parents[1]


class ASFRuntimeTests(unittest.TestCase):
    def test_draft_allowed(self):
        result = run_loop(
            ROOT / "examples" / "artifacts" / "draft_allowed.json",
            action="draft",
            policy_path=ROOT / "policies" / "default.yaml",
            root=ROOT,
            operator_authorized=True,
        )
        self.assertEqual(result["decision"]["status"], "pass")
        self.assertIsNone(result["wound"])

    def test_release_blocked_emits_wound(self):
        result = run_loop(
            ROOT / "examples" / "artifacts" / "release_blocked_missing_tests.json",
            action="release",
            policy_path=ROOT / "policies" / "default.yaml",
            root=ROOT,
            operator_authorized=True,
        )
        self.assertEqual(result["decision"]["status"], "missing_gate_failed")
        self.assertIsNotNone(result["wound"])
        self.assertEqual(result["wound"]["wound_class"], "missing_gate_failed")

    def test_rehydration_blocks_without_operator_authorization(self):
        result = run_loop(
            ROOT / "examples" / "artifacts" / "draft_allowed.json",
            action="draft",
            policy_path=ROOT / "policies" / "default.yaml",
            root=ROOT,
            operator_authorized=False,
        )
        self.assertEqual(result["decision"]["status"], "rehydration_failed")

    def test_ledger_record_created(self):
        result = run_loop(
            ROOT / "examples" / "artifacts" / "release_blocked_missing_tests.json",
            action="release",
            policy_path=ROOT / "policies" / "default.yaml",
            root=ROOT,
            operator_authorized=True,
        )
        self.assertEqual(result["ledger"]["schema"], "ASF-LEDGER-RECORD-v0.1")
        self.assertTrue(result["ledger"]["record_hash"])

    def test_ui_renders_geometry(self):
        result = run_loop(
            ROOT / "examples" / "artifacts" / "release_blocked_missing_tests.json",
            action="release",
            policy_path=ROOT / "policies" / "default.yaml",
            root=ROOT,
            operator_authorized=True,
        )
        self.assertIn("AI SURVIVAL FIELD RUNTIME", result["ui"])
        self.assertIn("WOUND PACKAGE", result["ui"])


if __name__ == "__main__":
    unittest.main()

