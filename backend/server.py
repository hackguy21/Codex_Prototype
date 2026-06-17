import json
import mimetypes
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from projects.global_news.config import delete_source, load_sources, upsert_source
from projects.global_news.models import SourceConfig
from projects.global_news.service import scrape_global_news
from projects.interest_pages.service import interest_pages_payload, update_interest_pages
from projects.korea_news.config import delete_site, load_sites, upsert_site
from projects.korea_news.models import SiteConfig
from projects.korea_news.service import scrape_news
from projects.korea_opinion.config import (
    delete_site as delete_opinion_site,
    load_sites as load_opinion_sites,
    upsert_site as upsert_opinion_site,
)
from projects.korea_opinion.service import scrape_opinion_news
from projects.traffic_monitor.config import delete_zone, load_zones, upsert_zone
from projects.traffic_monitor.models import ZoneConfig
from projects.traffic_monitor.service import monitor_provider, monitor_traffic
from projects.meta_project.automation import (
    automation_payload,
    start_automation_scheduler,
    update_automation_settings,
)
from projects.meta_project.config import project_catalog
from projects.meta_project.service import (
    scrape_selected_projects,
    scrape_selected_projects_and_send,
    scrape_selected_projects_gpt_and_send,
    settings_payload,
    update_settings,
)


ROOT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT_DIR / "frontend"


def safe_print(message: str) -> None:
    if sys.stdout:
        print(message)


class ProjectHormuzHandler(BaseHTTPRequestHandler):
    server_version = "ProjectHormuz/0.1"

    def do_GET(self) -> None:
        self._handle_api_request(self._do_GET)

    def do_POST(self) -> None:
        self._handle_api_request(self._do_POST)

    def do_DELETE(self) -> None:
        self._handle_api_request(self._do_DELETE)

    def _do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/projects":
            self._json(project_catalog(include_meta=True))
            return
        if parsed.path == "/api/meta_project/settings":
            self._json(settings_payload())
            return
        if parsed.path == "/api/meta_project/automation":
            self._json(automation_payload())
            return
        if parsed.path in {"/api/sites", "/api/korea_news/sites"}:
            self._json([site.to_dict() for site in load_sites()])
            return
        if parsed.path == "/api/global_news/sources":
            self._json([source.to_dict() for source in load_sources()])
            return
        if parsed.path == "/api/korea_opinion/sites":
            self._json([site.to_dict() for site in load_opinion_sites()])
            return
        if parsed.path == "/api/interest_pages/settings":
            self._json(interest_pages_payload())
            return
        if parsed.path == "/api/traffic_monitor/zones":
            self._json([zone.to_dict() for zone in load_zones()])
            return
        self._serve_static(parsed.path)

    def _do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in {"/api/sites", "/api/korea_news/sites"}:
            payload = self._read_json()
            site = SiteConfig.from_dict(payload)
            sites = upsert_site(site)
            self._json([item.to_dict() for item in sites], status=HTTPStatus.CREATED)
            return
        if parsed.path in {"/api/scrape", "/api/korea_news/scrape"}:
            payload = self._read_json(default={})
            max_articles = self._read_bounded_int(payload, "max_articles_per_site", default=15, minimum=1, maximum=50)
            self._json(scrape_news(max_articles_per_site=max_articles))
            return
        if parsed.path == "/api/meta_project/settings":
            payload = self._read_json(default={})
            self._json(update_settings(payload))
            return
        if parsed.path == "/api/meta_project/automation":
            payload = self._read_json(default={})
            self._json(update_automation_settings(payload))
            return
        if parsed.path == "/api/meta_project/scrape":
            payload = self._read_json(default={})
            self._json(scrape_selected_projects(payload))
            return
        if parsed.path == "/api/meta_project/scrape-and-send":
            payload = self._read_json(default={})
            try:
                self._json(scrape_selected_projects_and_send(payload))
            except (RuntimeError, ValueError) as exc:
                self._json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        if parsed.path == "/api/meta_project/scrape-gpt-and-send":
            payload = self._read_json(default={})
            try:
                self._json(scrape_selected_projects_gpt_and_send(payload))
            except (RuntimeError, ValueError) as exc:
                self._json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        if parsed.path == "/api/global_news/sources":
            payload = self._read_json()
            source = SourceConfig.from_dict(payload)
            sources = upsert_source(source)
            self._json([item.to_dict() for item in sources], status=HTTPStatus.CREATED)
            return
        if parsed.path == "/api/global_news/scrape":
            self._json(scrape_global_news())
            return
        if parsed.path == "/api/korea_opinion/sites":
            payload = self._read_json()
            site = SiteConfig.from_dict(payload)
            sites = upsert_opinion_site(site)
            self._json([item.to_dict() for item in sites], status=HTTPStatus.CREATED)
            return
        if parsed.path == "/api/korea_opinion/scrape":
            payload = self._read_json(default={})
            max_articles = self._read_bounded_int(payload, "max_articles_per_site", default=15, minimum=1, maximum=50)
            self._json(scrape_opinion_news(max_articles_per_site=max_articles))
            return
        if parsed.path == "/api/interest_pages/settings":
            payload = self._read_json(default={})
            self._json(update_interest_pages(payload))
            return
        if parsed.path == "/api/traffic_monitor/zones":
            payload = self._read_json()
            zone = ZoneConfig.from_dict(payload)
            zones = upsert_zone(zone)
            self._json([item.to_dict() for item in zones], status=HTTPStatus.CREATED)
            return
        if parsed.path == "/api/traffic_monitor/monitor":
            self._json(monitor_traffic())
            return
        if parsed.path == "/api/flightradar24/monitor":
            self._json(monitor_provider("flightradar24"))
            return
        if parsed.path == "/api/marine_traffic/monitor":
            self._json(monitor_provider("marinetraffic"))
            return
        self._json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def _do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/sites/") or parsed.path.startswith("/api/korea_news/sites/"):
            site_id = unquote(parsed.path.rsplit("/", 1)[-1])
            sites = delete_site(site_id)
            self._json([site.to_dict() for site in sites])
            return
        if parsed.path.startswith("/api/global_news/sources/"):
            source_id = unquote(parsed.path.rsplit("/", 1)[-1])
            sources = delete_source(source_id)
            self._json([source.to_dict() for source in sources])
            return
        if parsed.path.startswith("/api/korea_opinion/sites/"):
            site_id = unquote(parsed.path.rsplit("/", 1)[-1])
            sites = delete_opinion_site(site_id)
            self._json([site.to_dict() for site in sites])
            return
        if parsed.path.startswith("/api/traffic_monitor/zones/"):
            zone_id = unquote(parsed.path.rsplit("/", 1)[-1])
            zones = delete_zone(zone_id)
            self._json([zone.to_dict() for zone in zones])
            return
        self._json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args) -> None:
        safe_print(f"[{self.log_date_time_string()}] {format % args}")

    def _handle_api_request(self, handler) -> None:
        try:
            handler()
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
            if self._is_api_path():
                self._json({"error": str(exc) or "Invalid request"}, status=HTTPStatus.BAD_REQUEST)
                return
            raise

    def _is_api_path(self) -> bool:
        return urlparse(self.path).path.startswith("/api/")

    def _read_json(self, default=None):
        length = self._read_bounded_int(
            {"content-length": self.headers.get("content-length", "0")},
            "content-length",
            default=0,
            minimum=0,
            maximum=10_000_000,
        )
        if length == 0:
            return default if default is not None else {}
        raw = self.rfile.read(length).decode("utf-8")
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError("JSON body must be an object")
        return payload

    def _read_bounded_int(
        self,
        payload: dict,
        key: str,
        *,
        default: int,
        minimum: int,
        maximum: int,
    ) -> int:
        raw_value = payload.get(key, default)
        if raw_value is None or raw_value == "":
            raw_value = default
        try:
            value = int(raw_value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{key} must be an integer") from exc
        return max(minimum, min(value, maximum))

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
    port = 8000
    server = ThreadingHTTPServer((host, port), ProjectHormuzHandler)
    start_automation_scheduler()
    safe_print(f"Project Prototype running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
