from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse


@dataclass(slots=True)
class SiteConfig:
    id: str
    name: str
    url: str
    enabled: bool = True
    max_pages: int = 3
    page_param: str | None = "page"

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "SiteConfig":
        if not isinstance(raw, dict):
            raise ValueError("site config must be an object")

        url = str(raw.get("url", "")).strip()
        _validate_http_url(url)

        return cls(
            id=str(raw.get("id", "")).strip(),
            name=str(raw.get("name", "")).strip(),
            url=url,
            enabled=_parse_bool(raw.get("enabled", True)),
            max_pages=_parse_int(raw.get("max_pages", 3), default=3, minimum=1, maximum=10),
            page_param=_parse_page_param(raw.get("page_param", "page")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "enabled": self.enabled,
            "max_pages": self.max_pages,
            "page_param": self.page_param,
        }


@dataclass(slots=True)
class ArticleLink:
    title: str
    url: str
    source: str
    page: int
    score: int = 0


@dataclass(slots=True)
class ArticleSummary:
    title: str
    url: str
    source: str
    page: int
    summary: str
    published_at: str | None = None
    keywords: list[str] = field(default_factory=list)


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
            raise ValueError("max_pages must be an integer") from exc
    return max(minimum, min(parsed, maximum))


def _parse_page_param(value: Any) -> str | None:
    if value is None:
        return None
    page_param = str(value).strip()
    return page_param or None


def _validate_http_url(value: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("url must be an http(s) URL with a host")
