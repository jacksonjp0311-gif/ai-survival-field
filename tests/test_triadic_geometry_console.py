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
from asf.ui.geometry.gate_mapper import KNOWN_STATUSES, build_geometry_state, cli_panel, map_gates
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
        self.assertEqual(panel["wound_source"], "missing_gate")
        self.assertIsNone(panel["failed_gate_id"])

    def test_wound_panel_no_active_wound_without_wound(self):
        summary = dict(SAMPLE_SUMMARY)
        summary.pop("wound_package")
        panel = build_geometry_state(ROOT, summary).wound_panel
        self.assertEqual(panel["message"], "NO ACTIVE WOUND")

    def test_status_strip_contains_latest_version_and_ci(self):
        strip = build_geometry_state(ROOT, SAMPLE_SUMMARY).status_strip
        self.assertEqual(strip["latest_version"], "ASF-R v1.1.0-dev4")
        self.assertEqual(strip["ci_evidence_status"], "remote_pass")

    def test_legend_contains_neon_statuses(self):
        legend = build_geometry_state(ROOT, SAMPLE_SUMMARY).legend
        self.assertIn("pass", legend)
        self.assertIn("forbidden", legend)

    def test_cli_panel_is_read_only(self):
        panel = build_geometry_state(ROOT, SAMPLE_SUMMARY).cli_panel
        self.assertEqual(panel["mode"], "read_only_observe")
        self.assertEqual(panel["command"], "python -m asf.cli dogfood run")
        self.assertEqual(panel["title"], "LAST RUN TRACE")
        self.assertEqual(panel["panel_state"], "last_run_trace")

    def test_cli_panel_live_when_run_is_active(self):
        panel = cli_panel({"phase": "running", "exit_code": None, "stream": ["active event"]})
        self.assertEqual(panel["title"], "LIVE CLI RUN")
        self.assertEqual(panel["panel_state"], "active_run")
        self.assertTrue(panel["follow"])
        self.assertEqual(panel["stream"], ["active event"])

    def test_cli_panel_last_trace_when_run_is_complete(self):
        panel = cli_panel({"phase": "complete", "exit_code": 0, "stream": ["final event"]})
        self.assertEqual(panel["title"], "LAST RUN TRACE")
        self.assertEqual(panel["panel_state"], "last_run_trace")
        self.assertEqual(panel["stream"], ["final event"])

    def test_cli_panel_waits_when_no_run_exists(self):
        panel = cli_panel({})
        self.assertEqual(panel["title"], "NO ACTIVE RUN")
        self.assertEqual(panel["panel_state"], "no_active_run")
        self.assertEqual(panel["phase"], "waiting")
        self.assertIn("waiting", panel["stream"][0])

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
        self.assertIsNone(state.failed_gate_id)
        self.assertIsNone(state.wound_panel["failed_gate_id"])
        self.assertEqual(state.wound_panel["trace_source"], "synthetic_wound_source")

    def test_gate_12_pass_when_missing_gate_failed(self):
        state = build_geometry_state(ROOT, SAMPLE_SUMMARY)
        gate = next(item for item in state.gates if item["gate_id"] == 12)
        self.assertEqual(gate["status"], "pass")
        self.assertFalse(gate["failed"])
        self.assertFalse(gate["wound_linked"])

    def test_missing_gate_failed_uses_synthetic_wound_source(self):
        state = build_geometry_state(ROOT, SAMPLE_SUMMARY)
        self.assertEqual(state.wound_panel["wound_source"], "missing_gate")
        self.assertEqual(state.trace["source"], "synthetic_wound_source")
        self.assertEqual(state.wound_source_node["id"], "missing_gate_source")

    def test_wound_trace_does_not_start_from_passing_gate(self):
        state = build_geometry_state(ROOT, SAMPLE_SUMMARY)
        self.assertIsNone(state.trace["failed_gate_id"])
        self.assertFalse(any(gate["gate_id"] == 12 and gate["wound_linked"] for gate in state.gates))

    def test_closure_status_consistent_between_status_strip_and_wound_panel(self):
        state = build_geometry_state(ROOT, SAMPLE_SUMMARY)
        self.assertEqual(state.status_strip["closure_status"], state.wound_panel["closure_status"])
        self.assertEqual(state.status_strip["closure_status"], "closed")

    def test_closed_wound_trace_is_archived_not_active(self):
        state = build_geometry_state(ROOT, SAMPLE_SUMMARY)
        self.assertEqual(state.trace["mode"], "archived")
        self.assertEqual(state.trace["display"], "collapsed")

    def test_closed_wound_trace_display_collapsed(self):
        state = build_geometry_state(ROOT, SAMPLE_SUMMARY)
        self.assertEqual(state.trace["mode"], "archived")
        self.assertEqual(state.trace["display"], "collapsed")

    def test_open_wound_trace_is_active(self):
        summary = dict(SAMPLE_SUMMARY)
        summary.pop("closure_record")
        state = build_geometry_state(ROOT, summary)
        self.assertEqual(state.status_strip["closure_status"], "not closed")
        self.assertEqual(state.wound_panel["closure_status"], "not closed")
        self.assertEqual(state.trace["mode"], "active")
        self.assertEqual(state.trace["display"], "full")

    def test_active_wound_trace_display_full(self):
        summary = dict(SAMPLE_SUMMARY)
        summary.pop("closure_record")
        state = build_geometry_state(ROOT, summary)
        self.assertEqual(state.trace["display"], "full")

    def test_no_wound_trace_display_none(self):
        summary = dict(SAMPLE_SUMMARY)
        summary.pop("wound_package")
        state = build_geometry_state(ROOT, summary)
        self.assertEqual(state.trace["display"], "none")
        self.assertFalse(state.trace["visible"])

    def test_archived_wound_panel_uses_archived_language(self):
        panel = build_geometry_state(ROOT, SAMPLE_SUMMARY).wound_panel
        self.assertEqual(panel["record_label"], "ARCHIVED WOUND RECORD")
        self.assertEqual(panel["badge_label"], "ARCHIVED MISSING GATE CHECK")

    def test_active_wound_panel_uses_blocked_language(self):
        summary = dict(SAMPLE_SUMMARY)
        summary.pop("closure_record")
        panel = build_geometry_state(ROOT, summary).wound_panel
        self.assertEqual(panel["record_label"], "WOUND PACKAGE")
        self.assertEqual(panel["badge_label"], "")

    def test_gate_22_25_labels_have_top_band_offsets(self):
        state = build_geometry_state(ROOT, SAMPLE_SUMMARY)
        top_gates = [gate for gate in state.gates if gate["gate_id"] in {22, 23, 24, 25}]
        self.assertTrue(all(gate["label_y"] < 75 for gate in top_gates))

    def test_top_arc_labels_do_not_overlap_evidence_title(self):
        state = build_geometry_state(ROOT, SAMPLE_SUMMARY)
        top_gates = [gate for gate in state.gates if gate["gate_id"] in {22, 23, 24, 25}]
        evidence_title_y = 210
        self.assertTrue(all(gate["label_y"] < evidence_title_y - 80 for gate in top_gates))

    def test_geometry_events_are_read_only(self):
        events = geometry_events(ROOT)
        self.assertTrue(events)
        self.assertTrue(all(event["read_only"] for event in events))
        self.assertIn("heartbeat", {event["type"] for event in events})

    def test_ui_contains_live_cli_panel(self):
        html = (ROOT / "asf" / "ui" / "web" / "index.html").read_text(encoding="utf-8")
        self.assertIn("cli-panel-title", html)
        self.assertIn("LIVE CLI RUN", html)
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
        self.assertIn("circuit-trace", geometry)
        self.assertIn("circuit-pad", geometry)

    def test_archived_trace_does_not_render_long_circuit_path(self):
        geometry = (ROOT / "asf" / "ui" / "web" / "geometry.js").read_text(encoding="utf-8")
        self.assertIn('trace.display === "full"', geometry)
        self.assertIn("drawArchivedWoundMarker", geometry)

    def test_archived_trace_does_not_render_bright_circuit_pads(self):
        geometry = (ROOT / "asf" / "ui" / "web" / "geometry.js").read_text(encoding="utf-8")
        archived_branch = geometry.split("function drawArchivedWoundMarker", 1)[1]
        self.assertNotIn("circuit-pad", archived_branch)

    def test_missing_gate_source_label_hidden_when_archived(self):
        geometry = (ROOT / "asf" / "ui" / "web" / "geometry.js").read_text(encoding="utf-8")
        self.assertIn('if (mode !== "archived")', geometry)

    def test_eventsource_does_not_append_cli_lines_in_last_run_trace_mode(self):
        app = (ROOT / "asf" / "ui" / "web" / "app.js").read_text(encoding="utf-8")
        self.assertIn('latestState.cli_panel?.panel_state !== "active_run"', app)

    def test_eventsource_appends_cli_lines_only_in_active_run_mode(self):
        app = (ROOT / "asf" / "ui" / "web" / "app.js").read_text(encoding="utf-8")
        self.assertIn('panel_state !== "active_run"', app)
        self.assertIn("appendChild(row)", app)

    def test_geometry_server_exposes_state_json(self):
        server, thread, base = start_geometry_server()
        try:
            with urlopen(base + "/state.json", timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))
            self.assertEqual(data["schema"], "ASF-TRIADIC-GEOMETRY-STATE-v0.1")
        finally:
            server.shutdown()
            thread.join(timeout=5)

    def test_geometry_server_serves_cache_busted_index(self):
        server, thread, base = start_geometry_server()
        try:
            with urlopen(base + "/?v=test", timeout=5) as response:
                html = response.read().decode("utf-8")
            self.assertIn("ASF-R Triadic Geometry Console", html)
            self.assertIn("cli-panel-title", html)
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
