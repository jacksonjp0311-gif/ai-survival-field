import json
import unittest
from pathlib import Path

from asf.core.evolution_readiness import evaluate
from asf.core.forward_progress import classify_progress
from asf.core.repository_hygiene import scan_repository
from asf.core.runtime_geometry import CANONICAL_GEOMETRY, validate_geometry


ROOT = Path(__file__).resolve().parents[1]


class HermesPrimitiveTests(unittest.TestCase):
    def test_evolution_readiness_allows_repair_planner_with_unknown_tests(self):
        result = evaluate(
            test_status="unknown",
            open_wounds=["ASF-WOUND-1"],
            integration_closed=False,
            worktree_clean=False,
            requested_operation="repair_planner_dry_run",
            current_release_seal="docs/releases/ASF-R-v0.4-release-seal.json",
            current_enforcement_mode="enforce_block_only",
        )
        self.assertTrue(result.ready, result.blocked_reasons)

    def test_evolution_readiness_blocks_release_with_unknown_tests(self):
        result = evaluate(
            test_status="unknown",
            open_wounds=["ASF-WOUND-1"],
            integration_closed=False,
            worktree_clean=True,
            requested_operation="release",
            current_release_seal="docs/releases/ASF-R-v0.4-release-seal.json",
            current_enforcement_mode="enforce_block_only",
        )
        self.assertFalse(result.ready)
        self.assertIn("UNKNOWN_TEST_STATE", result.blocked_reasons)

    def test_forward_progress_allows_documentation(self):
        self.assertEqual(classify_progress("documentation")["status"], "permitted")

    def test_forward_progress_blocks_self_healing_mutation(self):
        self.assertEqual(classify_progress("self_healing_mutation")["status"], "blocked")

    def test_runtime_geometry_accepts_canonical(self):
        result = validate_geometry(list(CANONICAL_GEOMETRY))
        self.assertTrue(result["ok"], result)

    def test_runtime_geometry_detects_missing_stage(self):
        result = validate_geometry([stage for stage in CANONICAL_GEOMETRY if stage != "LEDGER-RECORD"])
        self.assertFalse(result["ok"])
        self.assertIn("LEDGER-RECORD", result["missing_stages"])

    def test_runtime_geometry_detects_order_drift(self):
        observed = list(CANONICAL_GEOMETRY)
        observed[1], observed[2] = observed[2], observed[1]
        result = validate_geometry(observed)
        self.assertFalse(result["ok"])
        self.assertTrue(result["order_drift"])

    def test_repository_hygiene_passes_current_repo(self):
        result = scan_repository(ROOT)
        self.assertTrue(result["ok"], result["errors"])

    def test_zero_context_latest_pointer_shape(self):
        pointer = json.loads((ROOT / "docs" / "context" / "latest-asf.json").read_text(encoding="utf-8"))
        for key in ["latest_version", "latest_release_seal", "remote_url", "test_count", "next_operation", "non_claim_lock"]:
            self.assertIn(key, pointer)

    def test_hermes_unknown_ci_fixture_blocks_release(self):
        fixture = json.loads((ROOT / "examples" / "hermes_lessons" / "hermes_unknown_ci_pointer.json").read_text(encoding="utf-8"))
        self.assertIn("release", fixture["blocked"])
        self.assertIn("adapter_dry_run", fixture["permitted"])

    def test_remote_provenance_seal_exists(self):
        seal = json.loads((ROOT / "docs" / "releases" / "ASF-R-v0.4.1-remote-provenance-seal.json").read_text(encoding="utf-8"))
        self.assertEqual(seal["push_status"], "success")


if __name__ == "__main__":
    unittest.main()
