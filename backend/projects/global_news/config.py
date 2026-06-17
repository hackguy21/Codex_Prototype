import json
import threading
from pathlib import Path

from .models import SourceConfig


ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "data" / "global_news"
SOURCES_PATH = DATA_DIR / "sources.json"
_SOURCES_LOCK = threading.RLock()

DEFAULT_SOURCES = [
    {
        "id": "nyt-world",
        "name": "New York Times - World",
        "provider": "rss",
        "feed_url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "enabled": True,
        "category": "international",
        "content_type": "news",
        "max_items": 10,
    },
    {
        "id": "nyt-opinion",
        "name": "New York Times - Opinion",
        "provider": "rss",
        "feed_url": "https://rss.nytimes.com/services/xml/rss/nyt/Opinion.xml",
        "enabled": True,
        "category": "opinion",
        "content_type": "opinion",
        "max_items": 10,
    },
    {
        "id": "bloomberg-politics",
        "name": "Bloomberg - Politics",
        "provider": "rss",
        "feed_url": "https://feeds.bloomberg.com/politics/news.rss",
        "enabled": True,
        "category": "international",
        "content_type": "news",
        "max_items": 10,
    },
    {
        "id": "bloomberg-opinion",
        "name": "Bloomberg - Opinion",
        "provider": "rss",
        "feed_url": "https://news.google.com/rss/search?q=site:bloomberg.com/opinion%20when:14d&hl=en-US&gl=US&ceid=US:en",
        "enabled": True,
        "category": "opinion",
        "content_type": "opinion",
        "max_items": 10,
    },
    {
        "id": "reuters-world",
        "name": "Reuters - World",
        "provider": "rss",
        "feed_url": "https://news.google.com/rss/search?q=site:reuters.com/world%20when:7d&hl=en-US&gl=US&ceid=US:en",
        "enabled": True,
        "category": "international",
        "content_type": "news",
        "max_items": 10,
    },
    {
        "id": "reuters-breakingviews",
        "name": "Reuters - Breakingviews",
        "provider": "rss",
        "feed_url": "https://news.google.com/rss/search?q=site:reuters.com/commentary/breakingviews%20when:30d&hl=en-US&gl=US&ceid=US:en",
        "enabled": True,
        "category": "opinion",
        "content_type": "opinion",
        "max_items": 10,
    },
]


def load_sources() -> list[SourceConfig]:
    with _SOURCES_LOCK:
        if not SOURCES_PATH.exists():
            sources = [SourceConfig.from_dict(item) for item in DEFAULT_SOURCES]
            save_sources(sources)
            return sources
        raw_sources = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
        return [SourceConfig.from_dict(item) for item in raw_sources]


def save_sources(sources: list[SourceConfig]) -> None:
    with _SOURCES_LOCK:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        payload = [source.to_dict() for source in sources]
        _write_json_atomic(SOURCES_PATH, payload)


def upsert_source(source: SourceConfig) -> list[SourceConfig]:
    if not source.id or not source.name or not source.feed_url:
        raise ValueError("id, name, feed_url are required")
    with _SOURCES_LOCK:
        sources = load_sources()
        for index, existing in enumerate(sources):
            if existing.id == source.id:
                sources[index] = source
                save_sources(sources)
                return sources
        sources.append(source)
        save_sources(sources)
        return sources


def delete_source(source_id: str) -> list[SourceConfig]:
    with _SOURCES_LOCK:
        sources = [source for source in load_sources() if source.id != source_id]
        save_sources(sources)
        return sources


def _write_json_atomic(path: Path, payload: object) -> None:
    temp_path = path.with_name(f"{path.name}.tmp")
    temp_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temp_path.replace(path)
