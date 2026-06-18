import json
import mimetypes
import os
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from projects.meta_project.config import project_catalog, settings_payload, update_settings


ROOT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT_DIR / "frontend"


def safe_print(message: str) -> None:
    if sys.stdout:
        print(message)


class ProjectPrototypeHandler(BaseHTTPRequestHandler):
    server_version = "ProjectPrototype/0.2"

    def do_GET(self) -> None:
        self._handle_request(self._do_GET)

    def do_POST(self) -> None:
        self._handle_request(self._do_POST)

    def _do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/projects":
            self._json(project_catalog(include_root=True))
            return
        if parsed.path == "/api/meta_project/settings":
            self._json(settings_payload())
            return
        self._serve_static(parsed.path)

    def _do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/meta_project/settings":
            self._json(update_settings(self._read_json(default={})))
            return
        self._json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args) -> None:
        safe_print(f"[{self.log_date_time_string()}] {format % args}")

    def _handle_request(self, handler) -> None:
        try:
            handler()
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
            if urlparse(self.path).path.startswith("/api/"):
                self._json({"error": str(exc) or "Invalid request"}, status=HTTPStatus.BAD_REQUEST)
                return
            raise

    def _read_json(self, default=None):
        length = int(self.headers.get("content-length", "0") or 0)
        if length == 0:
            return default if default is not None else {}
        if length > 1_000_000:
            raise ValueError("Request body is too large")
        payload = json.loads(self.rfile.read(length).decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("JSON body must be an object")
        return payload

    def _json(self, payload, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_static(self, path: str) -> None:
        relative = "index.html" if path in {"", "/"} else path.lstrip("/")
        file_path = (FRONTEND_DIR / relative).resolve()
        if not str(file_path).startswith(str(FRONTEND_DIR.resolve())) or not file_path.exists():
            self._json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)
            return

        content = file_path.read_bytes()
        content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def main() -> None:
    host = "127.0.0.1"
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer((host, port), ProjectPrototypeHandler)
    safe_print(f"Project Prototype running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
