from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ZoneConfig:
    id: str
    name: str
    region: str
    enabled: bool = True
    aircraft_enabled: bool = True
    vessel_enabled: bool = True
    refresh_minutes: int = 15
    notes: str = ""

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ZoneConfig":
        if not isinstance(raw, dict):
            raise ValueError("zone config must be an object")

        return cls(
            id=str(raw.get("id", "")).strip(),
            name=str(raw.get("name", "")).strip(),
            region=str(raw.get("region", "")).strip(),
            enabled=_parse_bool(raw.get("enabled", True)),
            aircraft_enabled=_parse_bool(raw.get("aircraft_enabled", True)),
            vessel_enabled=_parse_bool(raw.get("vessel_enabled", True)),
            refresh_minutes=_parse_int(raw.get("refresh_minutes", 15), default=15, minimum=5, maximum=240),
            notes=str(raw.get("notes", "")).strip(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "region": self.region,
            "enabled": self.enabled,
            "aircraft_enabled": self.aircraft_enabled,
            "vessel_enabled": self.vessel_enabled,
            "refresh_minutes": self.refresh_minutes,
            "notes": self.notes,
        }


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and value in {0, 1}:
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "y", "on"}:
            return True
        if normalized in {"false", "0", "no", "n", "off"}:
            return False
    raise ValueError("boolean fields must be true or false")


def _parse_int(value: Any, *, default: int, minimum: int, maximum: int) -> int:
    if value is None or value == "":
        parsed = default
    else:
        try:
            parsed = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("refresh_minutes must be an integer") from exc
    return max(minimum, min(parsed, maximum))
