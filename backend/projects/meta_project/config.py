import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "data" / "meta_project"
SETTINGS_PATH = DATA_DIR / "settings.json"

ROOT_PROJECT = {
    "id": "project_prototype",
    "name": "Project Prototype",
    "description": "바이브코딩에 사용되는 CSS/UI와 아키텍처의 프로토타입을 제공합니다",
    "order": 0,
    "category": "meta_project",
    "enabled": True,
}

DEFAULT_PROJECTS = [
    {
        "id": "summary_delivery",
        "name": "전체 프로젝트 요약",
        "description": "META PROJECT와 NORMAL PROJECT를 구분해 현재 프로젝트 구성을 요약합니다.",
        "order": 1,
        "category": "meta_project",
        "enabled": True,
    },
    {
        "id": "architecture_notes",
        "name": "코드구조 및 현재규칙",
        "description": "CSS/UI 패턴과 로컬 아키텍처 프로토타입의 구성 요소를 확인합니다.",
        "order": 2,
        "category": "meta_project",
        "enabled": True,
    },
    {
        "id": "information_send",
        "name": "수집정보 외부 전송",
        "description": "일반 프로젝트에서 수집한 정보를 외부로 전송합니다.",
        "order": 3,
        "category": "meta_project",
        "enabled": True,
    },
    {
        "id": "example_1",
        "name": "example_1",
        "description": "normal_project 아래에 추가되는 일반 프로젝트 예시입니다.",
        "order": 101,
        "category": "normal_project",
        "enabled": True,
    },
]

DEFAULT_SETTINGS = {"projects": DEFAULT_PROJECTS}


def settings_payload() -> dict:
    settings = load_settings()
    return {"projects": settings["projects"], "settings": settings}


def load_settings() -> dict:
    if not SETTINGS_PATH.exists():
        return save_settings(DEFAULT_SETTINGS)
    return _normalize_settings(json.loads(SETTINGS_PATH.read_text(encoding="utf-8")))


def save_settings(settings: dict) -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = _normalize_settings(settings)
    SETTINGS_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def update_settings(payload: dict) -> dict:
    current = load_settings()
    merged = {"projects": payload.get("projects", current["projects"])}
    saved = save_settings(merged)
    return {"projects": saved["projects"], "settings": saved}


def project_catalog(include_root: bool = False) -> list[dict]:
    projects = sorted(load_settings()["projects"], key=lambda item: item.get("order", 999))
    if include_root:
        return [ROOT_PROJECT.copy(), *projects]
    return projects


def _normalize_settings(settings: dict) -> dict:
    incoming_by_id = {
        str(project.get("id", "")).strip(): project
        for project in settings.get("projects", [])
        if str(project.get("id", "")).strip()
    }
    projects = []
    for default in DEFAULT_PROJECTS:
        incoming = incoming_by_id.get(default["id"], {})
        projects.append(
            {
                "id": default["id"],
                "name": str(incoming.get("name") or default["name"]).strip(),
                "description": str(incoming.get("description") or default["description"]).strip(),
                "order": _parse_int(incoming.get("order"), default["order"]),
                "category": default["category"],
                "enabled": _parse_bool(incoming.get("enabled"), default["enabled"]),
            }
        )
    return {"projects": projects}


def _parse_int(value: object, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(fallback)


def _parse_bool(value: object, fallback: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "on"}:
            return True
        if normalized in {"false", "0", "no", "off"}:
            return False
    if value is None:
        return bool(fallback)
    return bool(value)
