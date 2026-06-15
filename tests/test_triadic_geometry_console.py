import json
import subprocess
import sys
import threading
import unittest
from pathlib import Path
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from asf.ui.geometry.app import GeometryHandler, geometry_events
from asf.ui.geometry.gate_mapper import KNOWN_STATUSES, build_geometry_state, map_gates
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
        self.assertEqual(strip["latest_version"], "ASF-R v1.1.0-dev1")
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

    def test_full_loop_uses_cli_command_label(self):
        text = (ROOT / "asf" / "full_loop.py").read_text(encoding="utf-8")
        self.assertIn("python -m asf.cli full-loop run --geometry", text)

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
        seal = json.loads((ROOT / "docs" / "releases" / "ASF-R-v1.1.0-dev1-product-console-seal.json").read_text(encoding="utf-8"))
        self.assertEqual(seal["schema"], "ASF-OBSERVABILITY-SEAL-v1.1.0-dev1")
        self.assertFalse(seal["authority_expansion"])
        self.assertEqual(seal["gate_count"], 25)
        self.assertEqual(seal["ui_mode"], "read_only_observe")

    def test_geometry_state_gate_coordinates_exist(self):
        gate = build_geometry_state(ROOT, SAMPLE_SUMMARY).gates[11]
        for key in ["x", "y", "label_x", "label_y", "failed", "wound_linked"]:
            self.assertIn(key, gate)

    def test_geometry_state_known_statuses_only(self):
        statuses = {gate["status"] for gate in build_geometry_state(ROOT, SAMPLE_SUMMARY).gates}
        self.assertTrue(statuses <= KNOWN_STATUSES)

    def test_geometry_failed_gate_maps_to_wound_panel(self):
        state = build_geometry_state(ROOT, SAMPLE_SUMMARY)
        self.assertEqual(state.failed_gate_id, 12)
        self.assertEqual(state.wound_panel["failed_gate_id"], 12)

    def test_geometry_events_are_read_only(self):
        events = geometry_events(ROOT)
        self.assertTrue(events)
        self.assertTrue(all(event["read_only"] for event in events))
        self.assertIn("heartbeat", {event["type"] for event in events})

    def test_ui_contains_live_cli_panel(self):
        html = (ROOT / "asf" / "ui" / "web" / "index.html").read_text(encoding="utf-8")
        self.assertIn("Live CLI Run", html)
        self.assertIn("COMMAND (READ-ONLY)", html)

    def test_ui_contains_wound_package_panel(self):
        html = (ROOT / "asf" / "ui" / "web" / "index.html").read_text(encoding="utf-8")
        self.assertIn("Wound Package", html)
        self.assertIn("wound-panel", html)

    def test_ui_contains_status_cards(self):
        html = (ROOT / "asf" / "ui" / "web" / "index.html").read_text(encoding="utf-8")
        self.assertIn("status-cards", html)

    def test_ui_contains_header_badges(self):
        html = (ROOT / "asf" / "ui" / "web" / "index.html").read_text(encoding="utf-8")
        self.assertIn("READ-ONLY OBSERVE", html)
        self.assertIn("LOCAL RUNTIME", html)
        self.assertIn("FOLLOW MODE", html)

    def test_ui_has_no_authorize_repair_close_controls(self):
        html = (ROOT / "asf" / "ui" / "web" / "index.html").read_text(encoding="utf-8").lower()
        forbidden_controls = ["authorize repair", "execute repair", "close wound", "enable enforce_full"]
        for item in forbidden_controls:
            self.assertNotIn(item, html)

    def test_frontend_uses_events_endpoint(self):
        app = (ROOT / "asf" / "ui" / "web" / "app.js").read_text(encoding="utf-8")
        self.assertIn('new EventSource("/events")', app)

    def test_frontend_draws_wound_link(self):
        geometry = (ROOT / "asf" / "ui" / "web" / "geometry.js").read_text(encoding="utf-8")
        self.assertIn("drawWoundLink", geometry)
        self.assertIn("wound-link", geometry)

    def test_geometry_server_exposes_state_json(self):
        server, thread, base = start_geometry_server()
        try:
            with urlopen(base + "/state.json", timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))
            self.assertEqual(data["schema"], "ASF-TRIADIC-GEOMETRY-STATE-v0.1")
        finally:
            server.shutdown()
            thread.join(timeout=5)

    def test_geometry_server_exposes_events(self):
        server, thread, base = start_geometry_server()
        try:
            with urlopen(base + "/events", timeout=5) as response:
                text = response.read().decode("utf-8")
            self.assertIn("ASF-GEOMETRY-EVENT-v0.1", text)
            self.assertIn("event: heartbeat", text)
        finally:
            server.shutdown()
            thread.join(timeout=5)

    def test_geometry_server_has_no_post_mutation_endpoint(self):
        server, thread, base = start_geometry_server()
        try:
            request = Request(base + "/state.json", method="POST", data=b"{}")
            with self.assertRaises(HTTPError) as ctx:
                urlopen(request, timeout=5)
            self.assertEqual(ctx.exception.code, 405)
        finally:
            server.shutdown()
            thread.join(timeout=5)


def start_geometry_server():
    GeometryHandler.repo_root = ROOT
    server = ThreadingHTTPServer(("127.0.0.1", 0), GeometryHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    return server, thread, f"http://{host}:{port}"


if __name__ == "__main__":
    unittest.main()
