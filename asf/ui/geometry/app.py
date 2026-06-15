from __future__ import annotations

import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from asf.ui.geometry.gate_mapper import build_geometry_state


class GeometryHandler(SimpleHTTPRequestHandler):
    repo_root = Path(".").resolve()
    web_root = Path(__file__).resolve().parents[1] / "web"

    def do_GET(self) -> None:
        if self.path == "/state.json":
            payload = json.dumps(build_geometry_state(self.repo_root).as_dict(), indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        return super().do_GET()

    def translate_path(self, path: str) -> str:
        relative = path.lstrip("/") or "index.html"
        return str((self.web_root / relative).resolve())


def serve(root: str | Path = ".", *, host: str = "127.0.0.1", port: int = 8765) -> str:
    GeometryHandler.repo_root = Path(root).resolve()
    server = ThreadingHTTPServer((host, port), GeometryHandler)
    print(f"ASF-R Triadic Geometry Console: http://{host}:{port}")
    print("Mode: read_only_observe")
    server.serve_forever()
    return f"http://{host}:{port}"
