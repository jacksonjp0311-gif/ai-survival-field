import json
import subprocess
import sys
import unittest
from pathlib import Path

import asf


ROOT = Path(__file__).resolve().parents[1]


class CurrentHeadCISealTests(unittest.TestCase):
    def test_v092_current_head_ci_seal_shape(self):
        seal = json.loads((ROOT / "docs" / "releases" / "ASF-R-v0.9.2-current-head-ci-seal.json").read_text(encoding="utf-8"))
        self.assertEqual(seal["schema"], "ASF-REMOTE-CI-EVIDENCE-SEAL-v0.9.2")
        self.assertEqual(seal["head_sha"], "d6fe7ad2352fd789fb16a1d20ad76974dc41b1b2")
        self.assertEqual(seal["conclusion"], "success")

    def test_v092_current_head_artifact_digest_recorded(self):
        seal = json.loads((ROOT / "docs" / "releases" / "ASF-R-v0.9.2-current-head-ci-seal.json").read_text(encoding="utf-8"))
        self.assertTrue(seal["artifact_digest"].startswith("sha256:"))

    def test_v092_current_head_verified_steps_include_public_demo(self):
        seal = json.loads((ROOT / "docs" / "releases" / "ASF-R-v0.9.2-current-head-ci-seal.json").read_text(encoding="utf-8"))
        self.assertIn("Run public demo", seal["verified_steps"])

    def test_v092_current_head_keeps_enforce_full_disabled(self):
        seal = json.loads((ROOT / "docs" / "releases" / "ASF-R-v0.9.2-current-head-ci-seal.json").read_text(encoding="utf-8"))
        self.assertFalse(seal["enforce_full_enabled"])

    def test_v092_current_head_non_claim_lock(self):
        seal = json.loads((ROOT / "docs" / "releases" / "ASF-R-v0.9.2-current-head-ci-seal.json").read_text(encoding="utf-8"))
        self.assertIn("does not claim production security", seal["non_claim_lock"])


class V10PackagingTests(unittest.TestCase):
    def test_package_version_is_release_candidate(self):
        self.assertEqual(asf.__version__, "1.1.0.dev4")

    def test_pyproject_exposes_asf_console_script(self):
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('version = "1.1.0.dev4"', pyproject)
        self.assertIn('asf = "asf.cli:main"', pyproject)

    def test_readme_has_ci_badge(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("actions/workflows/asf-guard.yml/badge.svg", readme)

    def test_readme_states_v1_law(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("v1.0 does not expand authority", readme)

    def test_latest_pointer_identifies_v1_final(self):
        pointer = json.loads((ROOT / "docs" / "context" / "latest-asf.json").read_text(encoding="utf-8"))
        self.assertEqual(pointer["latest_version"], "ASF-R v1.1.0-dev4")
        self.assertEqual(pointer["current_state"], "TRIADIC_GEOMETRY_CONSOLE_CIRCULAR_ORBIT_POLISH")

    def test_install_doc_exists(self):
        text = (ROOT / "docs" / "install.md").read_text(encoding="utf-8")
        self.assertIn("python -m pip install -e .", text)

    def test_quickstart_doc_has_one_command_demo(self):
        text = (ROOT / "docs" / "quickstart.md").read_text(encoding="utf-8")
        self.assertIn("python -m asf.cli demo", text)

    def test_examples_walkthrough_mentions_blocked_release(self):
        text = (ROOT / "docs" / "examples_walkthrough.md").read_text(encoding="utf-8")
        self.assertIn("Blocked Release", text)

    def test_v10_release_criteria_forbids_enforce_full(self):
        text = (ROOT / "docs" / "v1_0_release_criteria.md").read_text(encoding="utf-8")
        self.assertIn("enforce_full", text)
        self.assertIn("must not enable", text)

    def test_v10_non_claim_lock_doc_exists(self):
        text = (ROOT / "docs" / "v1_0_non_claim_lock.md").read_text(encoding="utf-8")
        self.assertIn("does not prove truth", text)

    def test_v10_release_seal_shape(self):
        seal = json.loads((ROOT / "docs" / "releases" / "ASF-R-v1.0.0-release-seal.json").read_text(encoding="utf-8"))
        self.assertEqual(seal["schema"], "ASF-RELEASE-SEAL-v1.0.0")
        self.assertFalse(seal["authority_expansion"])

    def test_v10_release_seal_requires_remote_ci(self):
        seal = json.loads((ROOT / "docs" / "releases" / "ASF-R-v1.0.0-release-seal.json").read_text(encoding="utf-8"))
        self.assertEqual(seal["release_candidate_remote_ci"]["status"], "remote_pass")

    def test_v10_release_seal_preserves_bounded_mutation_only(self):
        seal = json.loads((ROOT / "docs" / "releases" / "ASF-R-v1.0.0-release-seal.json").read_text(encoding="utf-8"))
        self.assertEqual(seal["mutation_enabled"], "bounded_authorized_local_only")

    def test_v10_release_seal_keeps_self_healing_disabled(self):
        seal = json.loads((ROOT / "docs" / "releases" / "ASF-R-v1.0.0-release-seal.json").read_text(encoding="utf-8"))
        self.assertFalse(seal["self_healing_mutation_enabled"])

    def test_v10_release_seal_keeps_enforce_full_disabled(self):
        seal = json.loads((ROOT / "docs" / "releases" / "ASF-R-v1.0.0-release-seal.json").read_text(encoding="utf-8"))
        self.assertFalse(seal["enforce_full_enabled"])

    def test_v10_release_seal_has_one_command_demo(self):
        seal = json.loads((ROOT / "docs" / "releases" / "ASF-R-v1.0.0-release-seal.json").read_text(encoding="utf-8"))
        self.assertEqual(seal["one_command_demo"], "python -m asf.cli demo")

    def test_v10_release_seal_records_evidence_recursion_rule(self):
        seal = json.loads((ROOT / "docs" / "releases" / "ASF-R-v1.0.0-release-seal.json").read_text(encoding="utf-8"))
        self.assertIn("No commit is required to contain proof of its own future CI run", seal["post_release_ci_rule"])

    def test_v10_release_notes_public_claim(self):
        notes = (ROOT / "docs" / "releases" / "ASF-R-v1.0.0-release-notes.md").read_text(encoding="utf-8")
        self.assertIn("local evidence-gated control loop", notes)

    def test_public_demo_command_runs(self):
        result = subprocess.run(
            [sys.executable, "-m", "asf.cli", "demo"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ASF-PUBLIC-DEMO-v0.1", result.stdout)

    def test_dogfood_command_runs(self):
        result = subprocess.run(
            [sys.executable, "-m", "asf.cli", "dogfood", "run"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ASF-DOGFOOD-REPORT-v0.1", result.stdout)

    def test_blocked_release_still_fails_closed(self):
        result = subprocess.run(
            [sys.executable, "-m", "asf.cli", "enforce", "block-only", "examples/artifacts/release_blocked_missing_tests.json", "--action", "release"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=20,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("mutation_performed", result.stdout)

    def test_workflow_remains_read_only(self):
        workflow = (ROOT / ".github" / "workflows" / "asf-guard.yml").read_text(encoding="utf-8").lower()
        self.assertIn("contents: read", workflow)
        for token in ["git push", "gh release", "twine upload", "gh api"]:
            self.assertNotIn(token, workflow)

    def test_workflow_ci_evidence_uses_release_candidate_test_count(self):
        workflow = (ROOT / ".github" / "workflows" / "asf-guard.yml").read_text(encoding="utf-8")
        self.assertIn("--test-count 325", workflow)


if __name__ == "__main__":
    unittest.main()
