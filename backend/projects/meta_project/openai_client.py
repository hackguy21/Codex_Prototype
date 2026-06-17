import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT_DIR = Path(__file__).resolve().parents[3]
SECURE_DIR = ROOT_DIR / "data" / "meta_project" / "secure"
OPENAI_PATH = SECURE_DIR / "openai.json"
RESPONSES_URL = "https://api.openai.com/v1/responses"
DEFAULT_MODEL = "gpt-5.2"


def generate_card_news_report(result: dict) -> tuple[str, dict]:
    config = load_openai_config()
    api_key = config.get("api_key") or os.environ.get("OPENAI_API_KEY")
    model = config.get("model") or DEFAULT_MODEL
    if not api_key:
        raise ValueError("OpenAI API key is not configured. Set OPENAI_API_KEY or data/meta_project/secure/openai.json.")

    prompt = _build_prompt(result)
    payload = {
        "model": model,
        "instructions": (
            "You are a Korean financial-news editor. Convert collected news into compact Telegram card-news text. "
            "Do not include article body URLs. Do not use Markdown tables. Output Korean text only."
        ),
        "input": prompt,
        "reasoning": {"effort": "low"},
        "text": {"verbosity": "low"},
    }
    data = _openai_request(api_key, payload)
    text = _extract_output_text(data).strip()
    if not text:
        raise RuntimeError("OpenAI response did not include output text.")
    return text, {"model": model, "response_id": data.get("id")}


def load_openai_config() -> dict:
    if not OPENAI_PATH.exists():
        return {"api_key": "", "model": DEFAULT_MODEL}
    return json.loads(OPENAI_PATH.read_text(encoding="utf-8-sig"))


def _build_prompt(result: dict) -> str:
    items = []
    number = 1
    for project_result in result.get("results", []):
        project_name = project_result.get("project_name") or project_result.get("project_id") or "project"
        for article in project_result.get("result", {}).get("articles", []):
            items.append(
                {
                    "number": number,
                    "project": project_name,
                    "site": article.get("source") or "기타",
                    "title": article.get("title") or "",
                    "summary": article.get("summary") or "",
                    "original_title": article.get("original_title") or "",
                    "original_summary": article.get("original_summary") or "",
                }
            )
            number += 1

    return (
        "아래 JSON 배열의 뉴스를 텔레그램 카드뉴스용 한 줄 요약 목록으로 변환하세요.\n"
        "반드시 각 줄을 다음 형식으로만 작성하세요:\n"
        "<기사번호>.<기사제목> [<사이트이름>] <요약문>\n\n"
        "규칙:\n"
        "- 기사번호는 입력 number를 그대로 사용합니다.\n"
        "- 기사제목은 핵심만 남기되 원 제목 의미를 바꾸지 않습니다.\n"
        "- 사이트이름은 site 값을 사용합니다.\n"
        "- 요약문은 한국어 한 문장, 투자자가 빠르게 읽을 수 있게 압축합니다.\n"
        "- URL, 본문 링크, 프로젝트명, 불릿 기호, 추가 설명은 넣지 않습니다.\n"
        "- 각 기사는 한 줄만 사용합니다.\n\n"
        f"뉴스 JSON:\n{json.dumps(items, ensure_ascii=False, indent=2)}"
    )


def _openai_request(api_key: str, payload: dict) -> dict:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(RESPONSES_URL, data=body, method="POST")
    request.add_header("Authorization", f"Bearer {api_key}")
    request.add_header("Content-Type", "application/json")

    try:
        with urlopen(request, timeout=90) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        message = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API error: {message}") from exc
    except URLError as exc:
        raise RuntimeError(f"OpenAI connection error: {exc.reason}") from exc


def _extract_output_text(data: dict) -> str:
    if data.get("output_text"):
        return str(data["output_text"])

    chunks = []
    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                chunks.append(str(content["text"]))
    return "\n".join(chunks)
