import json
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .service import scrape_selected_projects_and_send


ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "data" / "meta_project"
AUTOMATION_PATH = DATA_DIR / "automation.json"
KST = timezone(timedelta(hours=9))
DEFAULT_AUTOMATION = {
    "enabled": False,
    "timezone": "Asia/Seoul",
    "times": [
        {"time": "09:00", "enabled": True},
        {"time": "18:00", "enabled": True},
    ],
}

_scheduler_started = False
_scheduler_lock = threading.Lock()
_run_lock = threading.Lock()
_last_run_keys: set[str] = set()
_last_result: dict | None = None


def load_automation_settings() -> dict:
    if not AUTOMATION_PATH.exists():
        save_automation_settings(DEFAULT_AUTOMATION)
    return _normalize_automation_settings(_read_automation_settings())


def save_automation_settings(settings: dict) -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = _normalize_automation_settings(settings)
    AUTOMATION_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def automation_payload() -> dict:
    return {
        "settings": load_automation_settings(),
        "last_result": _last_result,
    }


def update_automation_settings(payload: dict) -> dict:
    current = load_automation_settings()
    merged = {
        "enabled": payload.get("enabled", current["enabled"]),
        "timezone": "Asia/Seoul",
        "times": payload.get("times", current["times"]),
    }
    return automation_payload() | {"settings": save_automation_settings(merged)}


def start_automation_scheduler() -> None:
    global _scheduler_started
    with _scheduler_lock:
        if _scheduler_started:
            return
        _scheduler_started = True
        thread = threading.Thread(target=_scheduler_loop, name="meta-telegram-automation", daemon=True)
        thread.start()


def _scheduler_loop() -> None:
    while True:
        try:
            _run_due_schedule()
        except Exception as exc:  # noqa: BLE001 - background loop must stay alive.
            _record_last_result({"ok": False, "error": str(exc), "generated_at": _now_kst().isoformat()})
        time.sleep(20)


def _run_due_schedule() -> None:
    settings = load_automation_settings()
    if not settings["enabled"]:
        return

    now = _now_kst()
    current_time = now.strftime("%H:%M")
    for item in settings["times"]:
        if not item["enabled"] or item["time"] != current_time:
            continue
        run_key = f"{now.strftime('%Y-%m-%d')}T{current_time}"
        if run_key in _last_run_keys:
            continue
        _last_run_keys.add(run_key)
        _run_scheduled_send(run_key)


def _run_scheduled_send(run_key: str) -> None:
    global _last_result
    if not _run_lock.acquire(blocking=False):
        _record_last_result({"ok": False, "run_key": run_key, "error": "Previous automation run is still active."})
        return

    try:
        result = scrape_selected_projects_and_send()
        _record_last_result(
            {
                "ok": True,
                "run_key": run_key,
                "generated_at": result.get("generated_at"),
                "count": result.get("count", 0),
                "errors": result.get("errors", []),
                "telegram": result.get("telegram", {}),
            }
        )
    except Exception as exc:  # noqa: BLE001 - scheduled failures are surfaced in status.
        _record_last_result({"ok": False, "run_key": run_key, "error": str(exc), "generated_at": _now_kst().isoformat()})
    finally:
        _run_lock.release()


def _record_last_result(result: dict) -> None:
    global _last_result
    _last_result = result


def _read_automation_settings() -> dict:
    if not AUTOMATION_PATH.exists():
        return DEFAULT_AUTOMATION.copy()
    return json.loads(AUTOMATION_PATH.read_text(encoding="utf-8"))


def _normalize_automation_settings(settings: dict) -> dict:
    raw_times = settings.get("times") or DEFAULT_AUTOMATION["times"]
    times = []
    seen = set()
    for item in raw_times:
        value = str(item.get("time", "")).strip()
        if not _is_valid_time(value) or value in seen:
            continue
        seen.add(value)
        times.append({"time": value, "enabled": bool(item.get("enabled", True))})

    if not times:
        times = [item.copy() for item in DEFAULT_AUTOMATION["times"]]

    return {
        "enabled": bool(settings.get("enabled", DEFAULT_AUTOMATION["enabled"])),
        "timezone": "Asia/Seoul",
        "times": sorted(times, key=lambda item: item["time"]),
    }


def _is_valid_time(value: str) -> bool:
    try:
        datetime.strptime(value, "%H:%M")
    except ValueError:
        return False
    return len(value) == 5


def _now_kst() -> datetime:
    return datetime.now(KST)
