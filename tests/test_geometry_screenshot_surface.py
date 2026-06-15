import json
import subprocess
import sys
import unittest
import threading
from pathlib import Path
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from asf.ui.geometry.app import GeometryHandler
from asf.ui.geometry.gate_mapper import build_geometry_state
from asf.ui.geometry.screenshot import DEFAULT_SCREENSHOT, screenshot_metadata


ROOT = Path(__file__).resolve().parents[1]


class GeometryScreenshotSurfaceTests(unittest.TestCase):
    def test_readme_references_geometry_console_screenshot(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("![ASF-R Triadic Geometry Console](docs/assets/asf-r-triadic-geometry-console.png)", readme)

    def test_readme_contains_geometry_runtime_activation_commands(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(".\\scripts\\run-asf-full-loop.ps1 -Geometry", readme)
        self.assertIn("./scripts/run-asf-full-loop.sh --geometry", readme)
        self.assertIn("python -m asf.cli full-loop run --geometry", readme)

    def test_readme_contains_read_only_ui_law(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("The UI may observe.", readme)
        self.assertIn("The UI may not grant authority.", readme)

    def test_readme_contains_gate_color_legend(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for item in ["Green = pass", "Red = blocked/fail", "Amber = active/pending", "Cyan = read-only evidence"]:
            self.assertIn(item, readme)

    def test_readme_contains_25_gate_list(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("1. Latest Pointer Loaded", readme)
        self.assertIn("25. Closure Record Written", readme)

    def test_geometry_state_has_12_status_cards(self):
        state = build_geometry_state(ROOT).as_dict()
        self.assertEqual(len(state["status_strip"]), 12)

    def test_geometry_state_has_wound_panel(self):
        state = build_geometry_state(ROOT).as_dict()
        self.assertIn("wound_panel", state)
        self.assertIn("status", state["wound_panel"])

    def test_geometry_screenshot_metadata_shape(self):
        metadata = screenshot_metadata(output=ROOT / DEFAULT_SCREENSHOT, root=ROOT)
        self.assertEqual(metadata["schema"], "ASF-GEOMETRY-SCREENSHOT-METADATA-v0.1")
        self.assertEqual(metadata["geometry_screenshot_width"], 1280)
        self.assertEqual(metadata["geometry_screenshot_height"], 720)
        self.assertEqual(metadata["geometry_visual_check"]["gate_count"], 25)
        self.assertEqual(metadata["geometry_visual_check"]["status_card_count"], 12)

    def test_geometry_screenshot_artifact_exists_when_enabled(self):
        self.assertTrue((ROOT / DEFAULT_SCREENSHOT).exists())

    def test_geometry_screenshot_command_reports_artifact(self):
        result = subprocess.run(
            [sys.executable, "-m", "asf.cli", "geometry", "screenshot", "--output", str(DEFAULT_SCREENSHOT)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertTrue(data["geometry_screenshot_exists"])

    def test_geometry_server_rejects_post_with_405(self):
        server, thread, base = start_geometry_server()
        try:
            request = Request(base + "/events", method="POST", data=b"{}")
            with self.assertRaises(HTTPError) as ctx:
                urlopen(request, timeout=5)
            self.assertEqual(ctx.exception.code, 405)
        finally:
            server.shutdown()
            thread.join(timeout=5)

    def test_geometry_server_has_no_mutation_endpoints(self):
        routes = getattr(GeometryHandler, "MUTATION_ROUTES", [])
        self.assertEqual(routes, [])

    def test_full_loop_geometry_writes_summary(self):
        source = (ROOT / "asf" / "full_loop.py").read_text(encoding="utf-8")
        self.assertIn(".asf_loop_runs", source)
        self.assertIn("summary.json", source)
        self.assertIn("geometry_screenshot", source)

    def test_full_loop_geometry_summary_references_screenshot_when_available(self):
        source = (ROOT / "asf" / "full_loop.py").read_text(encoding="utf-8")
        self.assertIn("DEFAULT_SCREENSHOT", source)
        self.assertIn("geometry_screenshot_exists", source)

    def test_full_loop_geometry_preserves_enforce_full_false(self):
        source = (ROOT / "asf" / "full_loop.py").read_text(encoding="utf-8")
        self.assertIn('"enforce_full_enabled": False', source)

    def test_full_loop_geometry_preserves_self_healing_mutation_false(self):
        source = (ROOT / "asf" / "full_loop.py").read_text(encoding="utf-8")
        self.assertIn('"self_healing_mutation_enabled": False', source)

    def test_dev2_release_seal_shape(self):
        seal = json.loads((ROOT / "docs" / "releases" / "ASF-R-v1.1.0-dev2-geometry-screenshot-seal.json").read_text(encoding="utf-8"))
        self.assertEqual(seal["schema"], "ASF-OBSERVABILITY-SEAL-v1.1.0-dev2")
        self.assertFalse(seal["authority_expansion"])
        self.assertEqual(seal["gate_count"], 25)
        self.assertEqual(seal["status_card_count"], 12)


if __name__ == "__main__":
    unittest.main()


def start_geometry_server():
    GeometryHandler.repo_root = ROOT
    server = ThreadingHTTPServer(("127.0.0.1", 0), GeometryHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    return server, thread, f"http://{host}:{port}"
