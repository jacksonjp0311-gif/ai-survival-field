import json
import subprocess
import sys
import unittest
from pathlib import Path

from asf.ui.geometry.gate_mapper import build_geometry_state, map_gates
from asf.ui.geometry.schemas import NON_CLAIM_LOCK, READ_ONLY_UI_LAW


ROOT = Path(__file__).resolve().parents[1]


SAMPLE_SUMMARY = {
    "command": "python -m asf.cli dogfood run",
    "phase": "decision / wound / repair",
    "exit_code": 0,
    "follow": True,
    "rehydration_passed": True,
    "ledger_verified": True,
    "permission_ceiling": "residual_stratified",
    "artifact_validated": True,
    "decision": {
        "status": "missing_gate_failed",
        "permission_ceiling": "residual_stratified",
        "blocked_actions": ["release", "commit", "update_memory"],
        "permitted_actions": ["draft", "propose", "request_evidence"],
        "next_admissible_action": "acquire evidence",
    },
    "permission_checked": True,
    "block_enforcement_checked": True,
    "wound_package": {
        "wound_id": "ASF-WOUND-fde7366bae78",
        "wound_class": "missing_gate_failed",
    },
    "repair_plan": {"repair_plan_id": "ASF-REPAIR-1"},
    "repair_dry_run_passed": True,
    "repair_validation_passed": True,
    "repair_replay_passed": True,
    "authorization_receipt": {"authorization_receipt_id": "ASF-AUTH-1"},
    "authorization_bound": True,
    "bounded_repair_executed": True,
    "post_repair_evidence_captured": True,
    "closure_request": {"wound_id": "ASF-WOUND-fde7366bae78"},
    "closure_validation_passed": True,
    "closure_record": {"wound_closed": True},
}


class TriadicGeometryConsoleTests(unittest.TestCase):
    def test_read_only_law_forbids_authority(self):
        text = "\n".join(READ_ONLY_UI_LAW)
        self.assertIn("may not authorize repair", text)
        self.assertIn("may not execute mutation", text)
        self.assertIn("may not enable enforce_full", text)

    def test_non_claim_lock_forbids_repair_authority(self):
        self.assertIn("grant repair authority", NON_CLAIM_LOCK)

    def test_gate_mapper_has_25_gates(self):
        state = build_geometry_state(ROOT, SAMPLE_SUMMARY)
        self.assertEqual(len(state.gates), 25)

    def test_gate_labels_include_required_surface(self):
        labels = {gate["label"] for gate in build_geometry_state(ROOT, SAMPLE_SUMMARY).gates}
        self.assertIn("Latest Pointer Loaded", labels)
        self.assertIn("Closure Record Written", labels)

    def test_wound_panel_glows_blocked_when_wound_exists(self):
        panel = build_geometry_state(ROOT, SAMPLE_SUMMARY).wound_panel
        self.assertEqual(panel["status"], "blocked")
        self.assertEqual(panel["wound_id"], "ASF-WOUND-fde7366bae78")

    def test_wound_panel_no_active_wound_without_wound(self):
        summary = dict(SAMPLE_SUMMARY)
        summary.pop("wound_package")
        panel = build_geometry_state(ROOT, summary).wound_panel
        self.assertEqual(panel["message"], "NO ACTIVE WOUND")

    def test_status_strip_contains_latest_version_and_ci(self):
        strip = build_geometry_state(ROOT, SAMPLE_SUMMARY).status_strip
        self.assertEqual(strip["latest_version"], "ASF-R v1.1.0-dev0")
        self.assertEqual(strip["ci_evidence_status"], "remote_pass")

    def test_legend_contains_neon_statuses(self):
        legend = build_geometry_state(ROOT, SAMPLE_SUMMARY).legend
        self.assertIn("pass", legend)
        self.assertIn("forbidden", legend)

    def test_cli_panel_is_read_only(self):
        panel = build_geometry_state(ROOT, SAMPLE_SUMMARY).cli_panel
        self.assertEqual(panel["mode"], "read_only_observe")
        self.assertEqual(panel["command"], "python -m asf.cli dogfood run")

    def test_map_gates_marks_wound_emitted(self):
        gates = map_gates(ROOT, {"remote_url": "x", "remote_ci_status": "remote_pass", "non_claim_lock": "x"}, {"non_claim_lock": "x"}, SAMPLE_SUMMARY)
        by_id = {gate.gate_id: gate for gate in gates}
        self.assertEqual(by_id[15].status, "pass")

    def test_geometry_state_cli_command_runs(self):
        result = subprocess.run(
            [sys.executable, "-m", "asf.cli", "geometry", "state"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ASF-TRIADIC-GEOMETRY-STATE-v0.1", result.stdout)

    def test_web_assets_exist(self):
        for path in ["asf/ui/web/index.html", "asf/ui/web/app.js", "asf/ui/web/geometry.js", "asf/ui/web/styles.css"]:
            self.assertTrue((ROOT / path).exists(), path)

    def test_scripts_exist(self):
        self.assertTrue((ROOT / "scripts" / "run-asf-full-loop.ps1").exists())
        self.assertTrue((ROOT / "scripts" / "run-asf-full-loop.sh").exists())

    def test_scripts_call_full_loop_module(self):
        ps = (ROOT / "scripts" / "run-asf-full-loop.ps1").read_text(encoding="utf-8")
        sh = (ROOT / "scripts" / "run-asf-full-loop.sh").read_text(encoding="utf-8")
        self.assertIn("python -m asf.full_loop", ps)
        self.assertIn("python -m asf.full_loop", sh)

    def test_geometry_docs_include_full_loop_commands(self):
        text = (ROOT / "docs" / "geometry_console.md").read_text(encoding="utf-8")
        self.assertIn(".\\scripts\\run-asf-full-loop.ps1 -Geometry", text)
        self.assertIn("./scripts/run-asf-full-loop.sh --geometry", text)

    def test_sample_gate_trace_exists(self):
        trace = json.loads((ROOT / "examples" / "ui" / "sample_gate_trace.json").read_text(encoding="utf-8"))
        self.assertEqual(trace["schema"], "ASF-TRIADIC-GATE-TRACE-v0.1")

    def test_readme_contains_ui_geometry_section(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("ASF-R Triadic Geometry Console", text)
        self.assertIn("The UI may not grant authority.", text)

    def test_geometry_console_does_not_add_authority(self):
        state = build_geometry_state(ROOT, SAMPLE_SUMMARY).as_dict()
        self.assertEqual(state["mode"], "read_only_observe")
        self.assertIn("observes and illuminates", state["non_claim_lock"])

    def test_geometry_console_observability_seal_exists(self):
        seal = json.loads((ROOT / "docs" / "releases" / "ASF-R-v1.1.0-dev0-geometry-console-seal.json").read_text(encoding="utf-8"))
        self.assertEqual(seal["schema"], "ASF-OBSERVABILITY-SEAL-v1.1.0-dev0")
        self.assertFalse(seal["authority_expansion"])
        self.assertEqual(seal["gate_count"], 25)
        self.assertEqual(seal["test_count_minimum"], 252)


if __name__ == "__main__":
    unittest.main()
