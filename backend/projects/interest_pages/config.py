import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "data" / "interest_pages"
NOTES_PATH = DATA_DIR / "notes.json"

DEFAULT_NOTES = {
    "future_pages": "",
}


def load_notes() -> dict:
    if not NOTES_PATH.exists():
        save_notes(DEFAULT_NOTES)
    return _normalize_notes(json.loads(NOTES_PATH.read_text(encoding="utf-8")))


def save_notes(notes: dict) -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = _normalize_notes(notes)
    NOTES_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def _normalize_notes(notes: dict) -> dict:
    return {
        "future_pages": str(notes.get("future_pages", "")),
    }
