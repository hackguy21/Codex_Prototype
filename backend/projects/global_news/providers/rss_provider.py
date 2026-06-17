from common.http import fetch_text
from common.rss import parse_feed

from ..models import GlobalArticle, SourceConfig


def collect(source: SourceConfig) -> list[GlobalArticle]:
    fetched = fetch_text(source.feed_url)
    if fetched.status >= 400:
        raise RuntimeError(f"Feed returned HTTP {fetched.status}: {source.feed_url}")

    articles: list[GlobalArticle] = []
    for item in parse_feed(fetched.text)[: source.max_items]:
        if not item.title or not item.url:
            continue
        articles.append(
            GlobalArticle(
                title=item.title,
                url=item.url,
                source=item.source_name or source.name,
                source_id=source.id,
                provider=source.provider,
                category=source.category,
                content_type=source.content_type,
                summary=item.summary or "RSS feed did not include a summary.",
                published_at=item.published_at,
            )
        )
    return articles
