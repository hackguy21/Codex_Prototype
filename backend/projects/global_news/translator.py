import json
from functools import lru_cache
from urllib.parse import urlencode

from common.http import fetch_text


TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"


def translate_article(article):
    original_title = article.title
    original_summary = article.summary
    article.original_title = original_title
    article.original_summary = original_summary
    article.title = translate_to_korean(original_title)
    article.summary = translate_to_korean(original_summary)
    return article


@lru_cache(maxsize=512)
def translate_to_korean(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return text
    if _looks_korean(text):
        return text

    query = urlencode(
        {
            "client": "gtx",
            "sl": "auto",
            "tl": "ko",
            "dt": "t",
            "q": text[:1800],
        }
    )
    try:
        fetched = fetch_text(f"{TRANSLATE_URL}?{query}", timeout=10)
        payload = json.loads(fetched.text)
        translated = "".join(part[0] for part in payload[0] if part and part[0])
        return translated.strip() or text
    except Exception:
        return text


def _looks_korean(text: str) -> bool:
    korean_chars = sum(1 for char in text if "가" <= char <= "힣")
    return korean_chars >= max(4, len(text) // 5)
