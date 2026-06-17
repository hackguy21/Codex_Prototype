import json
import threading
from pathlib import Path

from projects.korea_news.models import SiteConfig


ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "data" / "korea_opinion"
SITES_PATH = DATA_DIR / "sites.json"
_SITES_LOCK = threading.RLock()


def load_sites() -> list[SiteConfig]:
    with _SITES_LOCK:
        if not SITES_PATH.exists():
            save_sites(default_sites())
        raw_sites = json.loads(SITES_PATH.read_text(encoding="utf-8"))
        return [SiteConfig.from_dict(item) for item in raw_sites]


def save_sites(sites: list[SiteConfig]) -> None:
    with _SITES_LOCK:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        payload = [site.to_dict() for site in sites]
        _write_json_atomic(SITES_PATH, payload)


def upsert_site(site: SiteConfig) -> list[SiteConfig]:
    if not site.id or not site.name or not site.url:
        raise ValueError("id, name, url are required")

    with _SITES_LOCK:
        sites = load_sites()
        for index, existing in enumerate(sites):
            if existing.id == site.id:
                sites[index] = site
                save_sites(sites)
                return sites

        sites.append(site)
        save_sites(sites)
        return sites


def delete_site(site_id: str) -> list[SiteConfig]:
    with _SITES_LOCK:
        sites = [site for site in load_sites() if site.id != site_id]
        save_sites(sites)
        return sites


def _write_json_atomic(path: Path, payload: object) -> None:
    temp_path = path.with_name(f"{path.name}.tmp")
    temp_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temp_path.replace(path)


def default_sites() -> list[SiteConfig]:
    return [
        SiteConfig(
            id="chosun-opinion-editorial",
            name="조선일보 - 오피니언",
            url="https://www.chosun.com/opinion/editorial/",
            enabled=True,
            max_pages=1,
            page_param=None,
        ),
        SiteConfig(
            id="donga-opinion",
            name="동아일보 - 오피니언",
            url="https://www.donga.com/news/List/Opinion",
            enabled=True,
            max_pages=1,
            page_param=None,
        ),
    ]
