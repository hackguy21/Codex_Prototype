import json
import threading
from pathlib import Path

from .models import ZoneConfig


ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "data" / "traffic_monitor"
ZONES_PATH = DATA_DIR / "zones.json"
_ZONES_LOCK = threading.RLock()

DEFAULT_ZONES = [
    {
        "id": "strait-of-hormuz",
        "name": "Strait of Hormuz",
        "region": "Hormuz",
        "enabled": True,
        "aircraft_enabled": True,
        "vessel_enabled": True,
        "refresh_minutes": 15,
        "notes": "Primary watch area for paired aviation and maritime snapshots.",
    }
]


def load_zones() -> list[ZoneConfig]:
    with _ZONES_LOCK:
        if not ZONES_PATH.exists():
            zones = [ZoneConfig.from_dict(item) for item in DEFAULT_ZONES]
            save_zones(zones)
            return zones
        raw_zones = json.loads(ZONES_PATH.read_text(encoding="utf-8"))
        return [ZoneConfig.from_dict(item) for item in raw_zones]


def save_zones(zones: list[ZoneConfig]) -> None:
    with _ZONES_LOCK:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        payload = [zone.to_dict() for zone in zones]
        _write_json_atomic(ZONES_PATH, payload)


def upsert_zone(zone: ZoneConfig) -> list[ZoneConfig]:
    if not zone.id or not zone.name or not zone.region:
        raise ValueError("id, name, region are required")

    with _ZONES_LOCK:
        zones = load_zones()
        for index, existing in enumerate(zones):
            if existing.id == zone.id:
                zones[index] = zone
                save_zones(zones)
                return zones
        zones.append(zone)
        save_zones(zones)
        return zones


def delete_zone(zone_id: str) -> list[ZoneConfig]:
    with _ZONES_LOCK:
        zones = [zone for zone in load_zones() if zone.id != zone_id]
        save_zones(zones)
        return zones


def _write_json_atomic(path: Path, payload: object) -> None:
    temp_path = path.with_name(f"{path.name}.tmp")
    temp_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temp_path.replace(path)
