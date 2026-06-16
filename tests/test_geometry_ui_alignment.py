import json
import unittest
from pathlib import Path

from asf.ui.geometry.gate_mapper import build_geometry_state


ROOT = Path(__file__).resolve().parents[1]


class GeometryUIAlignmentTests(unittest.TestCase):
    def test_geometry_has_25_gates(self):
        self.assertEqual(len(build_geometry_state(ROOT).gates), 25)

    def test_geometry_has_12_footer_cards(self):
        self.assertEqual(len(build_geometry_state(ROOT).status_strip), 12)

    def test_cli_panel_scroll_container_exists(self):
        html = (ROOT / "asf" / "ui" / "web" / "index.html").read_text(encoding="utf-8")
        self.assertIn("cli-stream", html)
        self.assertIn('class="stream cli-stream"', html)

    def test_wound_panel_scroll_container_exists(self):
        html = (ROOT / "asf" / "ui" / "web" / "index.html").read_text(encoding="utf-8")
        self.assertIn("wound-body", html)
        self.assertIn('class="wound-fields wound-body"', html)

    def test_cli_scroll_container_uses_custom_scrollbar_styles(self):
        css = (ROOT / "asf" / "ui" / "web" / "styles.css").read_text(encoding="utf-8")
        self.assertIn(".cli-stream::-webkit-scrollbar", css)
        self.assertIn("scrollbar-width: thin", css)

    def test_wound_scroll_container_uses_custom_scrollbar_styles(self):
        css = (ROOT / "asf" / "ui" / "web" / "styles.css").read_text(encoding="utf-8")
        self.assertIn(".wound-body::-webkit-scrollbar", css)
        self.assertIn("scrollbar-color: #2f5374", css)

    def test_footer_no_overflow_at_1280x720_contract(self):
        css = (ROOT / "asf" / "ui" / "web" / "styles.css").read_text(encoding="utf-8")
        self.assertIn("grid-template-rows: 72px minmax(0, 1fr) 96px", css)
        self.assertIn("overflow: hidden", css)

    def test_wound_panel_constrained_above_footer(self):
        css = (ROOT / "asf" / "ui" / "web" / "styles.css").read_text(encoding="utf-8")
        self.assertIn("grid-template-rows: minmax(318px, 0.58fr) minmax(188px, 0.42fr)", css)
        self.assertIn(".wound-panel", css)

    def test_header_badges_render_in_single_row(self):
        css = (ROOT / "asf" / "ui" / "web" / "styles.css").read_text(encoding="utf-8")
        self.assertIn(".top-badges { display: flex; align-items: center; gap: 12px; justify-self: end; }", css)

    def test_failed_gate_connector_renders(self):
        js = (ROOT / "asf" / "ui" / "web" / "geometry.js").read_text(encoding="utf-8")
        self.assertIn("drawWoundLink", js)
        self.assertIn("circuit-trace", js)
        self.assertIn("circuit-pad", js)
        self.assertIn("H${midX}", js)

    def test_geometry_labels_have_computed_orbit_model(self):
        mapper = (ROOT / "asf" / "ui" / "geometry" / "gate_mapper.py").read_text(encoding="utf-8")
        self.assertIn("GEOMETRY_CENTER", mapper)
        self.assertIn("GATE_ORBIT_RADIUS", mapper)
        self.assertIn("gate_angle", mapper)

    def test_dev4_release_seal_shape(self):
        seal = json.loads((ROOT / "docs" / "releases" / "ASF-R-v1.1.0-dev4-circular-orbit-seal.json").read_text(encoding="utf-8"))
        self.assertEqual(seal["schema"], "ASF-OBSERVABILITY-SEAL-v1.1.0-dev4")
        self.assertFalse(seal["authority_expansion"])
        self.assertFalse(seal["enforce_full_enabled"])
        self.assertEqual(seal["geometry_constraints"]["gate_orbit"], "single_shared_circle")


if __name__ == "__main__":
    unittest.main()
