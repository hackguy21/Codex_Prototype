from datetime import datetime, timezone

from projects.global_news.config import load_sources
from projects.korea_news.config import load_sites as load_korea_sites
from projects.korea_opinion.config import load_sites as load_opinion_sites

from .config import load_notes, save_notes


def interest_pages_payload() -> dict:
    return {
        "notes": load_notes(),
        "sources": _current_sources(),
    }


def update_interest_pages(payload: dict) -> dict:
    return {
        "notes": save_notes(payload.get("notes", payload)),
        "sources": _current_sources(),
    }


def interest_pages_snapshot() -> dict:
    sources = _current_sources()
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(sources),
        "errors": [],
        "articles": [],
        "sources": sources,
    }


def _current_sources() -> list[dict]:
    sources = []
    for site in load_korea_sites():
        sources.append(
            {
                "project_id": "korea_news",
                "project_name": "korea_tech_news",
                "source_id": site.id,
                "name": site.name,
                "url": site.url,
                "method": "크롤링",
                "enabled": site.enabled,
                "detail": f"{site.max_pages}페이지 / page param: {site.page_param or '없음'}",
            }
        )

    for source in load_sources():
        sources.append(
            {
                "project_id": "global_news",
                "project_name": "global_news",
                "source_id": source.id,
                "name": source.name,
                "url": source.feed_url,
                "method": source.provider.upper(),
                "enabled": source.enabled,
                "detail": f"{source.category} / {source.content_type} / {source.max_items}개",
            }
        )

    for site in load_opinion_sites():
        sources.append(
            {
                "project_id": "korea_opinion",
                "project_name": "korea_opinion",
                "source_id": site.id,
                "name": site.name,
                "url": site.url,
                "method": "크롤링",
                "enabled": site.enabled,
                "detail": f"{site.max_pages}페이지 / page param: {site.page_param or '없음'}",
            }
        )

    return sources
