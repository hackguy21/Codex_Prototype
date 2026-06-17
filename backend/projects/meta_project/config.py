import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "data" / "meta_project"
SETTINGS_PATH = DATA_DIR / "settings.json"

META_PROJECT = {
    "id": "meta_project",
    "name": "모니터링 관제",
    "description": "구역 모니터링 실행 대상과 텔레그램 전송 흐름을 관리합니다.",
    "order": 0,
    "enabled": True,
    "category": "meta_project",
}

DEFAULT_NAV_CATEGORIES = [
    {
        "id": "daily_monitor",
        "name": "Daily Monitor",
        "description": "매일 확인하는 모니터링 프로젝트",
        "order": 1,
        "collapsed": False,
    },
]

DEFAULT_PROJECTS = [
    {
        "id": "daily_news_manager",
        "name": "수집 및 요약 / 전송",
        "description": "Daily Monitor 프로젝트의 수집 및 요약, 텔레그램 전송 흐름을 관리합니다.",
        "order": 1,
        "enabled": True,
        "category": "meta_project",
    },
    {
        "id": "other_manager",
        "name": "기타",
        "description": "Project Hormuz의 코드 구조와 백엔드 경계를 확인합니다.",
        "order": 2,
        "enabled": True,
        "category": "meta_project",
    },
    {
        "id": "flightradar24",
        "name": "FlightRadar24",
        "description": "호르무즈 구역 항공 트래픽 모니터링 스캐폴드",
        "order": 10,
        "enabled": True,
        "category": "project",
        "nav_category": "daily_monitor",
    },
    {
        "id": "marine_traffic",
        "name": "MarineTraffic",
        "description": "호르무즈 구역 해상 트래픽 모니터링 스캐폴드",
        "order": 11,
        "enabled": True,
        "category": "project",
        "nav_category": "daily_monitor",
    },
]

DEFAULT_SETTINGS = {
    "selected_projects": ["flightradar24", "marine_traffic"],
    "projects": DEFAULT_PROJECTS,
    "nav_categories": DEFAULT_NAV_CATEGORIES,
}


def load_settings() -> dict:
    if not SETTINGS_PATH.exists():
        save_settings(DEFAULT_SETTINGS)
    return _normalize_settings(_read_settings())


def save_settings(settings: dict) -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = _normalize_settings(settings)
    SETTINGS_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def project_catalog(include_meta: bool = False) -> list[dict]:
    projects = sorted(load_settings()["projects"], key=lambda item: item.get("order", 999))
    if include_meta:
        return [META_PROJECT.copy(), *projects]
    return projects


def _read_settings() -> dict:
    if not SETTINGS_PATH.exists():
        return DEFAULT_SETTINGS.copy()
    return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))


def _normalize_settings(settings: dict) -> dict:
    nav_categories = _normalize_nav_categories(settings.get("nav_categories", DEFAULT_NAV_CATEGORIES))
    valid_nav_category_ids = {category["id"] for category in nav_categories}

    defaults = {project["id"]: project for project in DEFAULT_PROJECTS}
    incoming_projects = settings.get("projects", [])
    incoming_by_id = {
        str(project.get("id", "")).strip(): project
        for project in incoming_projects
        if str(project.get("id", "")).strip() in defaults
    }

    projects = []
    for project_id, default in defaults.items():
        incoming = incoming_by_id.get(project_id, {})
        project = {
            "id": project_id,
            "name": str(incoming.get("name") or default["name"]).strip(),
            "description": str(incoming.get("description") or default["description"]).strip(),
            "order": _parse_int(incoming.get("order"), default["order"]),
            "enabled": _parse_bool(incoming.get("enabled"), default["enabled"]),
            "category": default["category"],
        }
        if default["category"] == "project":
            project["nav_category"] = _normalize_nav_category(
                incoming.get("nav_category") or default.get("nav_category"),
                valid_nav_category_ids,
            )
        projects.append(project)

    valid_ids = {
        project["id"]
        for project in projects
        if project.get("enabled", True) and project.get("category") == "project"
    }
    selected = settings.get("selected_projects", DEFAULT_SETTINGS["selected_projects"])
    selected_projects = [project_id for project_id in selected if project_id in valid_ids]

    return {
        "selected_projects": selected_projects,
        "projects": projects,
        "nav_categories": nav_categories,
    }


def _normalize_nav_categories(categories: list[dict]) -> list[dict]:
    defaults = {category["id"]: category for category in DEFAULT_NAV_CATEGORIES}
    incoming_by_id = {
        str(category.get("id", "")).strip(): category
        for category in categories
        if str(category.get("id", "")).strip() in defaults
    }

    normalized = []
    for category_id, default in defaults.items():
        incoming = incoming_by_id.get(category_id, {})
        normalized.append(
            {
                "id": category_id,
                "name": str(incoming.get("name") or default["name"]).strip(),
                "description": str(incoming.get("description") or default["description"]).strip(),
                "order": _parse_int(incoming.get("order"), default["order"]),
                "collapsed": _parse_bool(incoming.get("collapsed"), default["collapsed"]),
            }
        )
    return sorted(normalized, key=lambda item: item.get("order", 999))


def _normalize_nav_category(value: str | None, valid_ids: set[str]) -> str:
    candidate = str(value or "daily_monitor").strip()
    if candidate in valid_ids:
        return candidate
    return "daily_monitor"


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
