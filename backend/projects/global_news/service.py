from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from common.news_article import NewsArticle

from .config import load_sources
from .models import GlobalArticle
from .providers import rss_provider
from .translator import translate_article


PROVIDERS = {
    "rss": rss_provider.collect,
}


def scrape_global_news() -> dict:
    articles = []
    errors = []
    generated_at = datetime.now(timezone.utc).isoformat()

    for source in load_sources():
        if not source.enabled:
            continue
        collector = PROVIDERS.get(source.provider)
        if not collector:
            errors.append({"source": source.name, "message": f"Unsupported provider: {source.provider}"})
            continue
        try:
            articles.extend(collector(source))
        except Exception as exc:  # noqa: BLE001 - API reports per-source failures.
            errors.append({"source": source.name, "message": str(exc)})

    with ThreadPoolExecutor(max_workers=8) as executor:
        articles = list(executor.map(translate_article, articles))

    articles.sort(key=lambda article: (article.source, article.content_type, article.title))
    return {
        "generated_at": generated_at,
        "count": len(articles),
        "errors": errors,
        "articles": [_article_record(article, generated_at).to_dict() for article in articles],
    }


def _article_record(article: GlobalArticle, collected_at: str) -> NewsArticle:
    return NewsArticle(
        id=None,
        project_id="global_news",
        source_id=article.source_id,
        source_name=article.source,
        title=article.title,
        url=article.url,
        published_at=article.published_at,
        collected_at=collected_at,
        summary=article.summary,
        body=None,
        original_title=article.original_title,
        original_summary=article.original_summary,
        language="ko",
        category=article.category,
        content_type=article.content_type,
        metadata={"provider": article.provider},
    )
