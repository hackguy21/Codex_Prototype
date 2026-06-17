from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from common.news_article import NewsArticle

from .config import load_sites
from .extractor import extract_article, extract_links, page_url
from .fetcher import fetch_html
from .models import ArticleLink, ArticleSummary, SiteConfig
from .summarizer import extract_keywords, summarize


def scrape_news(max_articles_per_site: int = 15) -> dict:
    sites = [site for site in load_sites() if site.enabled]
    results: list[ArticleSummary] = []
    errors: list[dict[str, str]] = []
    generated_at = datetime.now(timezone.utc).isoformat()

    for site in sites:
        try:
            links = _collect_site_links(site, max_articles=max_articles_per_site)
            results.extend(_summarize_links(links))
        except Exception as exc:  # noqa: BLE001 - API should report per-site failures.
            errors.append({"site": site.name, "message": str(exc)})

    return {
        "generated_at": generated_at,
        "count": len(results),
        "errors": errors,
        "articles": [_article_record(article, generated_at).to_dict() for article in results],
    }


def _collect_site_links(site: SiteConfig, max_articles: int) -> list[ArticleLink]:
    collected: list[ArticleLink] = []
    seen: set[str] = set()

    for page in range(1, site.max_pages + 1):
        url = page_url(site.url, page, site.page_param)
        fetched = fetch_html(url)
        if fetched.status >= 400:
            continue
        links = extract_links(fetched.html, fetched.url, site.name, page)
        for link in links:
            if link.url in seen:
                continue
            seen.add(link.url)
            collected.append(link)
            if len(collected) >= max_articles:
                return collected

    return collected


def _summarize_links(links: list[ArticleLink]) -> list[ArticleSummary]:
    summaries: list[ArticleSummary | None] = [None] * len(links)
    with ThreadPoolExecutor(max_workers=6) as executor:
        future_map = {executor.submit(_summarize_link, link): (index, link) for index, link in enumerate(links)}
        for future in as_completed(future_map):
            index, link = future_map[future]
            try:
                summaries[index] = future.result()
            except Exception:
                summaries[index] = _error_summary(link)

    return [summary for summary in summaries if summary is not None]


def _summarize_link(link: ArticleLink) -> ArticleSummary:
    fetched = fetch_html(link.url)
    if fetched.status >= 400:
        return _error_summary(link, f"기사 본문을 가져오지 못했습니다. HTTP {fetched.status}")

    article = extract_article(fetched.html)
    title = article.get("title") or link.title
    body = article.get("body") or article.get("description") or link.title
    return ArticleSummary(
        title=str(title),
        url=link.url,
        source=link.source,
        page=link.page,
        summary=summarize(str(body)),
        published_at=article.get("published_at"),
        keywords=extract_keywords(str(body), limit=5),
    )


def _error_summary(link: ArticleLink, message: str = "기사 본문을 가져오지 못했습니다.") -> ArticleSummary:
    return ArticleSummary(
        title=link.title,
        url=link.url,
        source=link.source,
        page=link.page,
        summary=message,
        keywords=[],
    )


def _article_record(article: ArticleSummary, collected_at: str) -> NewsArticle:
    return NewsArticle(
        id=None,
        project_id="korea_news",
        source_id=None,
        source_name=article.source,
        title=article.title,
        url=article.url,
        published_at=article.published_at,
        collected_at=collected_at,
        summary=article.summary,
        body=None,
        language="ko",
        category="technology",
        content_type="news",
        metadata={"page": article.page, "keywords": article.keywords},
    )
