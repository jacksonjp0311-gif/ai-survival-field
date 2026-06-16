import math
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from asf.ui.geometry.gate_mapper import build_geometry_state
from asf.ui.geometry.schemas import READ_ONLY_UI_LAW
from tests.test_geometry_screenshot_surface import start_geometry_server


ROOT = Path(__file__).resolve().parents[1]


class GeometryCircularOrbitTests(unittest.TestCase):
    def state(self):
        return build_geometry_state(ROOT).as_dict()

    def test_gate_coordinates_share_same_center(self):
        state = self.state()
        self.assertEqual(state["geometry"]["center_x"], 490)
        self.assertEqual(state["geometry"]["center_y"], 345)

    def test_gate_coordinates_share_same_radius(self):
        state = self.state()
        cx = state["geometry"]["center_x"]
        cy = state["geometry"]["center_y"]
        radius = state["geometry"]["gate_orbit_radius"]
        for gate in state["gates"]:
            actual = math.hypot(gate["x"] - cx, gate["y"] - cy)
            self.assertLessEqual(abs(actual - radius), 0.75, gate)

    def test_gate_orbit_has_25_unique_angles(self):
        angles = [gate["angle_deg"] for gate in self.state()["gates"]]
        self.assertEqual(len(angles), 25)
        self.assertEqual(len(set(angles)), 25)

    def test_triangle_uses_same_geometry_center(self):
        state = self.state()
        cx = state["geometry"]["center_x"]
        cy = state["geometry"]["center_y"]
        radius = state["geometry"]["triangle_radius"]
        for vertex in state["geometry"]["triangle_vertices"].values():
            actual = math.hypot(vertex["x"] - cx, vertex["y"] - cy)
            self.assertLessEqual(abs(actual - radius), 0.75, vertex)

    def test_gate_labels_have_multiline_support(self):
        gates = self.state()["gates"]
        self.assertTrue(all(gate["label_lines"] for gate in gates))
        self.assertIn("Post-Repair Evidence", gates[21]["label_lines"])

    def test_gate_labels_have_anchor_metadata(self):
        anchors = {gate["label_anchor"] for gate in self.state()["gates"]}
        self.assertTrue(anchors <= {"start", "middle", "end"})
        self.assertIn("start", anchors)
        self.assertIn("end", anchors)

    def test_failed_gate_has_circuit_trace_route(self):
        js = (ROOT / "asf" / "ui" / "web" / "geometry.js").read_text(encoding="utf-8")
        css = (ROOT / "asf" / "ui" / "web" / "styles.css").read_text(encoding="utf-8")
        self.assertIn("circuit-trace", js)
        self.assertIn("circuit-pad", js)
        self.assertIn("Q${midX + 8}", js)
        self.assertIn(".circuit-trace", css)
        self.assertIn(".circuit-pad", css)

    def test_footer_status_cards_do_not_clip_values(self):
        css = (ROOT / "asf" / "ui" / "web" / "styles.css").read_text(encoding="utf-8")
        self.assertIn("overflow: visible", css)
        self.assertIn("overflow-wrap: anywhere", css)
        self.assertIn("word-break: break-word", css)
        self.assertIn("max-height: none", css)

    def test_footer_has_12_status_cards(self):
        self.assertEqual(len(self.state()["status_strip"]), 12)

    def test_cli_scrollbar_css_present(self):
        css = (ROOT / "asf" / "ui" / "web" / "styles.css").read_text(encoding="utf-8")
        self.assertIn(".cli-stream::-webkit-scrollbar", css)

    def test_wound_scrollbar_css_present(self):
        css = (ROOT / "asf" / "ui" / "web" / "styles.css").read_text(encoding="utf-8")
        self.assertIn(".wound-body::-webkit-scrollbar", css)

    def test_wound_panel_constrained_above_footer(self):
        css = (ROOT / "asf" / "ui" / "web" / "styles.css").read_text(encoding="utf-8")
        self.assertIn("grid-template-rows: minmax(318px, 0.58fr) minmax(188px, 0.42fr)", css)

    def test_screenshot_artifact_updated(self):
        screenshot = ROOT / "docs" / "assets" / "asf-r-triadic-geometry-console.png"
        self.assertTrue(screenshot.exists())
        self.assertGreater(screenshot.stat().st_size, 100000)

    def test_read_only_boundary_preserved(self):
        text = "\n".join(READ_ONLY_UI_LAW)
        self.assertIn("may not authorize repair", text)
        self.assertIn("may not execute mutation", text)
        self.assertIn("may not grant authority", text)

    def test_post_rejected_with_405(self):
        server, thread, base = start_geometry_server()
        try:
            request = Request(base + "/state.json", method="POST", data=b"{}")
            with self.assertRaises(HTTPError) as ctx:
                urlopen(request, timeout=5)
            self.assertEqual(ctx.exception.code, 405)
        finally:
            server.shutdown()
            thread.join(timeout=5)

    def test_no_mutation_endpoints_exist(self):
        html = (ROOT / "asf" / "ui" / "web" / "index.html").read_text(encoding="utf-8").lower()
        for forbidden in ["authorize repair", "execute repair", "close wound", "enable enforce_full"]:
            self.assertNotIn(forbidden, html)


if __name__ == "__main__":
    unittest.main()
