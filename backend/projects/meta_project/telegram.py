import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT_DIR = Path(__file__).resolve().parents[3]
SECURE_DIR = ROOT_DIR / "data" / "meta_project" / "secure"
TELEGRAM_PATH = SECURE_DIR / "telegram.json"
MESSAGE_LIMIT = 3900


def send_telegram_report(text: str) -> dict:
    config = load_telegram_config()
    api_key = config.get("api_key")
    if not api_key:
        raise ValueError("Telegram API key is not configured.")

    chat_id = config.get("chat_id") or discover_chat_id(api_key)
    if not chat_id:
        raise ValueError("Telegram chat_id를 찾지 못했습니다. 먼저 해당 봇에게 아무 메시지나 보내주세요.")

    config["chat_id"] = chat_id
    save_telegram_config(config)

    chunks = _message_chunks(text)
    sent_messages = []
    for chunk in chunks:
        sent_messages.append(_send_message(api_key, chat_id, chunk))

    return {
        "chat_id": str(chat_id),
        "message_count": len(sent_messages),
    }


def load_telegram_config() -> dict:
    if not TELEGRAM_PATH.exists():
        return {"api_key": "", "chat_id": None}
    return json.loads(TELEGRAM_PATH.read_text(encoding="utf-8"))


def save_telegram_config(config: dict) -> None:
    SECURE_DIR.mkdir(parents=True, exist_ok=True)
    TELEGRAM_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def discover_chat_id(api_key: str) -> str | None:
    data = _telegram_request(api_key, "getUpdates", {})
    updates = data.get("result", [])
    for update in reversed(updates):
        message = update.get("message") or update.get("channel_post") or {}
        chat = message.get("chat") or {}
        chat_id = chat.get("id")
        if chat_id is not None:
            return str(chat_id)
    return None


def _send_message(api_key: str, chat_id: str, text: str) -> dict:
    return _telegram_request(
        api_key,
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": "true",
        },
    )


def _telegram_request(api_key: str, method: str, payload: dict) -> dict:
    url = f"https://api.telegram.org/bot{api_key}/{method}"
    body = urlencode(payload).encode("utf-8")
    request = Request(url, data=body, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        message = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Telegram API error: {message}") from exc
    except URLError as exc:
        raise RuntimeError(f"Telegram connection error: {exc.reason}") from exc

    if not data.get("ok"):
        raise RuntimeError(f"Telegram API error: {data.get('description', 'unknown error')}")
    return data


def _message_chunks(text: str) -> list[str]:
    if len(text) <= MESSAGE_LIMIT:
        return [text]

    chunks = []
    current = []
    current_size = 0
    for line in text.splitlines():
        line_size = len(line) + 1
        if current and current_size + line_size > MESSAGE_LIMIT:
            chunks.append("\n".join(current))
            current = []
            current_size = 0
        current.append(line)
        current_size += line_size
    if current:
        chunks.append("\n".join(current))
    return chunks
