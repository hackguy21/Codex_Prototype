import re
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0 Safari/537.36 NewsScraperBot/1.0"
)


@dataclass(slots=True)
class FetchResult:
    url: str
    text: str
    status: int = 200


def fetch_text(url: str, timeout: int = 12) -> FetchResult:
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read()
            charset = _detect_charset(response.headers.get("content-type", ""), body)
            return FetchResult(
                url=response.geturl(),
                text=body.decode(charset, errors="replace"),
                status=getattr(response, "status", 200),
            )
    except HTTPError as exc:
        body = exc.read()
        charset = _detect_charset(exc.headers.get("content-type", ""), body)
        return FetchResult(url=url, text=body.decode(charset, errors="replace"), status=exc.code)
    except URLError as exc:
        raise RuntimeError(f"Failed to fetch {url}: {exc.reason}") from exc


def _detect_charset(content_type: str, body: bytes) -> str:
    header_match = re.search(r"charset=([\w-]+)", content_type, flags=re.I)
    if header_match:
        return header_match.group(1)
    head = body[:4000].decode("ascii", errors="ignore")
    meta_match = re.search(r"<meta[^>]+charset=[\"']?([\w-]+)", head, flags=re.I)
    if meta_match:
        return meta_match.group(1)
    return "utf-8"
