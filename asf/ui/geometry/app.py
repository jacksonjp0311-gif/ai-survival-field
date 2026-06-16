from __future__ import annotations

import json
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from asf.ui.geometry.gate_mapper import build_geometry_state


def geometry_events(root: str | Path = ".") -> list[dict]:
    state = build_geometry_state(root).as_dict()
    events = [{
        "schema": "ASF-GEOMETRY-EVENT-v0.1",
        "timestamp": "now",
        "type": "summary",
        "message": "Geometry state loaded read-only",
        "read_only": True,
    }]
    for gate in state["gates"]:
        if gate["status"] in {"pass", "blocked", "fail", "pending"}:
            events.append({
                "schema": "ASF-GEOMETRY-EVENT-v0.1",
                "timestamp": "now",
                "type": "gate_status",
                "gate_id": gate["gate_id"],
                "gate_label": gate["label"],
                "status": gate["status"],
                "message": f"{gate['label']} -> {gate['status']}",
                "read_only": True,
            })
    for line in state["cli_panel"]["stream"]:
        events.append({
            "schema": "ASF-GEOMETRY-EVENT-v0.1",
            "timestamp": "now",
            "type": "cli_line",
            "message": line,
            "read_only": True,
        })
    if state["wound_panel"].get("status") == "blocked":
        events.append({
            "schema": "ASF-GEOMETRY-EVENT-v0.1",
            "timestamp": "now",
            "type": "wound",
            "gate_id": state.get("failed_gate_id"),
            "status": "blocked",
            "message": "Wound package linked to failed gate",
            "read_only": True,
        })
    events.append({
        "schema": "ASF-GEOMETRY-EVENT-v0.1",
        "timestamp": "now",
        "type": "heartbeat",
        "message": "read-only heartbeat",
        "read_only": True,
    })
    return events


class GeometryHandler(SimpleHTTPRequestHandler):
    repo_root = Path(".").resolve()
    web_root = Path(__file__).resolve().parents[1] / "web"

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        if path in {"", "/"}:
            payload = (self.web_root / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        if path == "/state.json":
            payload = json.dumps(build_geometry_state(self.repo_root).as_dict(), indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        if path == "/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            for event in geometry_events(self.repo_root):
                payload = json.dumps(event, sort_keys=True)
                self.wfile.write(f"event: {event['type']}\n".encode("utf-8"))
                self.wfile.write(f"data: {payload}\n\n".encode("utf-8"))
                self.wfile.flush()
                time.sleep(0.01)
            return
        return super().do_GET()

    def do_POST(self) -> None:
        self.send_response(405)
        self.send_header("Allow", "GET")
        self.end_headers()

    def translate_path(self, path: str) -> str:
        relative = urlsplit(path).path.lstrip("/") or "index.html"
        return str((self.web_root / relative).resolve())


def serve(root: str | Path = ".", *, host: str = "127.0.0.1", port: int = 8765) -> str:
    GeometryHandler.repo_root = Path(root).resolve()
    server = ThreadingHTTPServer((host, port), GeometryHandler)
    print(f"ASF-R Triadic Geometry Console: http://{host}:{port}")
    print("Mode: read_only_observe")
    server.serve_forever()
    return f"http://{host}:{port}"
