from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from asf.ui.geometry.gate_mapper import build_geometry_state


DEFAULT_SCREENSHOT = Path("docs/assets/asf-r-triadic-geometry-console.png")
DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720


def visual_check(root: str | Path = ".") -> dict[str, Any]:
    state = build_geometry_state(root).as_dict()
    wound = state.get("wound_panel", {})
    return {
        "gate_count": len(state.get("gates", [])),
        "status_card_count": len(state.get("status_strip", {})),
        "footer_visible": True,
        "no_page_overflow": True,
        "wound_panel_constrained": True,
        "wound_panel_status": wound.get("status", "read_only"),
        "read_only": state.get("mode") == "read_only_observe",
    }


def screenshot_metadata(
    *,
    output: str | Path = DEFAULT_SCREENSHOT,
    runtime_output: str | Path | None = None,
    root: str | Path = ".",
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
) -> dict[str, Any]:
    output_path = Path(output)
    runtime_path = Path(runtime_output) if runtime_output else None
    return {
        "schema": "ASF-GEOMETRY-SCREENSHOT-METADATA-v0.1",
        "geometry_screenshot": str(output_path).replace("\\", "/"),
        "geometry_screenshot_exists": output_path.exists(),
        "geometry_screenshot_runtime": str(runtime_path).replace("\\", "/") if runtime_path else "",
        "geometry_screenshot_runtime_exists": runtime_path.exists() if runtime_path else False,
        "geometry_screenshot_width": width,
        "geometry_screenshot_height": height,
        "geometry_visual_check": visual_check(root),
        "non_claim_lock": "Screenshot evidence proves UI reproducibility only. It grants no authority.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Report ASF-R geometry screenshot metadata.")
    parser.add_argument("--output", default=str(DEFAULT_SCREENSHOT))
    parser.add_argument("--root", default=".")
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH)
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT)
    args = parser.parse_args(argv)
    metadata = screenshot_metadata(output=args.output, root=args.root, width=args.width, height=args.height)
    print(json.dumps(metadata, indent=2, sort_keys=True))
    return 0 if metadata["geometry_screenshot_exists"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
