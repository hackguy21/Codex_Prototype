import html
import re
from html.parser import HTMLParser
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse

from .models import ArticleLink


ARTICLE_HINTS = (
    "news",
    "article",
    "view",
    "read",
    "mainnews",
    "zdnet.co.kr/view/",
    "theguru.co.kr/news/article",
    "finance.naver.com/news/",
    "kipost.net/news/article",
    "chosun.com/opinion/",
    "donga.com/news/",
)
BLOCKED_HINTS = (
    "javascript:",
    "mailto:",
    "#",
    "login",
    "member",
    "search",
    "rss",
    "facebook",
    "twitter",
    "instagram",
    "youtube",
    "archive.chosun.com",
    "newslibrary.chosun.com",
)
INVESTING_TERMS = (
    "반도체",
    "AI",
    "인공지능",
    "실적",
    "매출",
    "영업익",
    "주가",
    "증시",
    "투자",
    "공시",
    "수주",
    "공급",
    "계약",
    "삼성",
    "SK",
    "엔비디아",
    "테슬라",
    "미국",
    "중국",
)


class LinkParser(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._title_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        attr_map = {key.lower(): value or "" for key, value in attrs}
        self._href = attr_map.get("href")
        self._title_parts = [attr_map.get("title", ""), attr_map.get("aria-label", "")]

    def handle_data(self, data: str) -> None:
        if self._href:
            self._title_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or not self._href:
            return
        title = clean_text(" ".join(self._title_parts))
        url = urljoin(self.base_url, html.unescape(self._href))
        self.links.append((title, url))
        self._href = None
        self._title_parts = []


class ArticleParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.description = ""
        self.published_at = None
        self._in_title = False
        self._capture_text = False
        self._skip_depth = 0
        self._title_parts: list[str] = []
        self._body_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attr_map = {key.lower(): value or "" for key, value in attrs}

        if tag in {"script", "style", "noscript", "nav", "footer", "header", "aside"}:
            self._skip_depth += 1
            return

        if tag == "title":
            self._in_title = True

        if tag == "meta":
            name = (attr_map.get("name") or attr_map.get("property") or "").lower()
            content = clean_text(attr_map.get("content", ""))
            if name in {"description", "og:description"} and content and not self.description:
                self.description = content
            if name in {"article:published_time", "og:regdate"} and content:
                self.published_at = content

        if tag in {"p", "h1"}:
            self._capture_text = True

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        if self._in_title:
            self._title_parts.append(data)
        if self._capture_text:
            self._body_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self._skip_depth and tag in {"script", "style", "noscript", "nav", "footer", "header", "aside"}:
            self._skip_depth -= 1
            return
        if tag == "title":
            self._in_title = False
        if tag in {"p", "h1"}:
            self._capture_text = False
            self._body_parts.append("\n")

    def result(self) -> dict[str, str | None]:
        title = clean_text(" ".join(self._title_parts))
        title = re.split(r"\s[-|:]\s", title)[0].strip() or title
        body = clean_text("\n".join(self._body_parts))
        return {
            "title": title,
            "description": self.description,
            "published_at": self.published_at,
            "body": body,
        }


def page_url(base_url: str, page: int, page_param: str | None) -> str:
    if not page_param:
        return base_url
    parsed = urlparse(base_url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query[page_param] = str(page)
    return urlunparse(parsed._replace(query=urlencode(query, doseq=True)))


def extract_links(html_text: str, base_url: str, source: str, page: int, limit: int = 12) -> list[ArticleLink]:
    parser = LinkParser(base_url)
    parser.feed(html_text)

    seen: set[str] = set()
    candidates: list[ArticleLink] = []
    for title, url in parser.links:
        if not _looks_like_article(title, url):
            continue
        normalized = _strip_tracking(url)
        if normalized in seen:
            continue
        seen.add(normalized)
        score = _score_link(title, normalized)
        candidates.append(ArticleLink(title=title, url=normalized, source=source, page=page, score=score))

    candidates.sort(key=lambda item: item.score, reverse=True)
    return candidates[:limit]


def extract_article(html_text: str) -> dict[str, str | None]:
    parser = ArticleParser()
    parser.feed(html_text)
    return parser.result()


def clean_text(value: str) -> str:
    value = html.unescape(value)
    value = re.sub(r"[\t\r\f\v]+", " ", value)
    value = re.sub(r" {2,}", " ", value)
    value = re.sub(r"\n{2,}", "\n", value)
    return value.strip()


def _looks_like_article(title: str, url: str) -> bool:
    lowered_url = url.lower()
    if any(hint in lowered_url for hint in BLOCKED_HINTS):
        return False
    if len(title) < 8:
        return False
    if "chosun.com/opinion/" in lowered_url:
        return bool(re.search(r"/opinion/.+/\d{4}/\d{2}/\d{2}/", lowered_url))
    if "donga.com/news/" in lowered_url:
        return "/article/" in lowered_url
    if not any(hint in lowered_url for hint in ARTICLE_HINTS):
        return False
    return True


def _score_link(title: str, url: str) -> int:
    score = min(len(title), 80)
    score += sum(15 for term in INVESTING_TERMS if term.lower() in title.lower())
    score += 20 if re.search(r"\d", url) else 0
    score += 10 if "article" in url.lower() or "view" in url.lower() else 0
    return score


def _strip_tracking(url: str) -> str:
    parsed = urlparse(url)
    query = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if not key.lower().startswith(("utm_", "fbclid", "gclid"))
    ]
    return urlunparse(parsed._replace(fragment="", query=urlencode(query, doseq=True)))
