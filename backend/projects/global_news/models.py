from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse


@dataclass(slots=True)
class SourceConfig:
    id: str
    name: str
    provider: str
    feed_url: str
    enabled: bool = True
    category: str = "international"
    content_type: str = "news"
    max_items: int = 10

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "SourceConfig":
        if not isinstance(raw, dict):
            raise ValueError("source config must be an object")

        feed_url = str(raw.get("feed_url", "")).strip()
        _validate_http_url(feed_url)

        return cls(
            id=str(raw.get("id", "")).strip(),
            name=str(raw.get("name", "")).strip(),
            provider=str(raw.get("provider", "rss")).strip() or "rss",
            feed_url=feed_url,
            enabled=_parse_bool(raw.get("enabled", True)),
            category=str(raw.get("category", "international")).strip() or "international",
            content_type=str(raw.get("content_type", "news")).strip() or "news",
            max_items=_parse_int(raw.get("max_items", 10), default=10, minimum=1, maximum=50),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "provider": self.provider,
            "feed_url": self.feed_url,
            "enabled": self.enabled,
            "category": self.category,
            "content_type": self.content_type,
            "max_items": self.max_items,
        }


@dataclass(slots=True)
class GlobalArticle:
    title: str
    url: str
    source: str
    source_id: str | None
    provider: str
    category: str
    content_type: str
    summary: str
    published_at: str | None = None
    original_title: str | None = None
    original_summary: str | None = None


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and value in {0, 1}:
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "y", "on"}:
            return True
        if normalized in {"false", "0", "no", "n", "off"}:
            return False
    raise ValueError("enabled must be a boolean")


def _parse_int(value: Any, *, default: int, minimum: int, maximum: int) -> int:
    if value is None or value == "":
        parsed = default
    else:
        try:
            parsed = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("max_items must be an integer") from exc
    return max(minimum, min(parsed, maximum))


def _validate_http_url(value: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("feed_url must be an http(s) URL with a host")
