import re
from collections import Counter


STOPWORDS = {
    "그리고",
    "그러나",
    "하지만",
    "있는",
    "했다",
    "한다",
    "대한",
    "지난",
    "이번",
    "관련",
    "위해",
    "통해",
    "다고",
    "다고 밝혔다",
}


def summarize(text: str, max_sentences: int = 3, max_chars: int = 420) -> str:
    sentences = split_sentences(text)
    if not sentences:
        return "본문을 충분히 추출하지 못했습니다."
    if len(sentences) <= max_sentences:
        return trim(" ".join(sentences), max_chars)

    keywords = extract_keywords(text)
    ranked = []
    for index, sentence in enumerate(sentences):
        score = sum(3 for word in keywords if word in sentence)
        score += 2 if re.search(r"\d+[%조억원만달러]*", sentence) else 0
        score += max(0, 4 - index)
        ranked.append((score, index, sentence))

    selected = sorted(ranked, reverse=True)[:max_sentences]
    ordered = [sentence for _, _, sentence in sorted(selected, key=lambda item: item[1])]
    return trim(" ".join(ordered), max_chars)


def extract_keywords(text: str, limit: int = 8) -> list[str]:
    words = re.findall(r"[가-힣A-Za-z0-9]{2,}", text)
    words = [word for word in words if word not in STOPWORDS and not word.isdigit()]
    counter = Counter(words)
    return [word for word, _ in counter.most_common(limit)]


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    chunks = re.split(r"(?<=[.!?。])\s+", text)
    return [chunk.strip() for chunk in chunks if len(chunk.strip()) >= 20]


def trim(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "…"
