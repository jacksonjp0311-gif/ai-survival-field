import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RemoteCIEvidenceSealTests(unittest.TestCase):
    def test_v091_remote_ci_seal_shape(self):
        seal = json.loads((ROOT / "docs" / "releases" / "ASF-R-v0.9.1-remote-ci-evidence-seal.json").read_text(encoding="utf-8"))
        self.assertEqual(seal["schema"], "ASF-REMOTE-CI-EVIDENCE-SEAL-v0.9.1")
        self.assertEqual(seal["conclusion"], "success")
        self.assertEqual(seal["artifact_name"], "asf-ci-evidence")

    def test_latest_pointer_remote_ci_pass(self):
        pointer = json.loads((ROOT / "docs" / "context" / "latest-asf.json").read_text(encoding="utf-8"))
        self.assertEqual(pointer["remote_ci_status"], "remote_pass")
        self.assertEqual(pointer["remote_ci_run_id"], 27547977961)

    def test_remote_ci_artifact_digest_recorded(self):
        pointer = json.loads((ROOT / "docs" / "context" / "latest-asf.json").read_text(encoding="utf-8"))
        self.assertTrue(pointer["remote_ci_artifact_digest"].startswith("sha256:"))

    def test_remote_ci_non_claim_lock(self):
        seal = json.loads((ROOT / "docs" / "releases" / "ASF-R-v0.9.1-remote-ci-evidence-seal.json").read_text(encoding="utf-8"))
        self.assertIn("does not claim production security", seal["non_claim_lock"])

    def test_remote_ci_steps_include_dogfood(self):
        seal = json.loads((ROOT / "docs" / "releases" / "ASF-R-v0.9.1-remote-ci-evidence-seal.json").read_text(encoding="utf-8"))
        self.assertIn("Run dogfood report", seal["verified_steps"])


if __name__ == "__main__":
    unittest.main()
