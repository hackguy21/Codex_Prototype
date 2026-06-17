from datetime import datetime, timezone

from .config import load_zones


PROVIDERS = {
    "flightradar24": {
        "label": "FlightRadar24",
        "enabled_field": "aircraft_enabled",
        "summary": "Flight snapshot capture adapter is not implemented yet.",
    },
    "marinetraffic": {
        "label": "MarineTraffic",
        "enabled_field": "vessel_enabled",
        "summary": "Marine snapshot capture adapter is not implemented yet.",
    },
}


def monitor_traffic() -> dict:
    return _monitor_provider(None)


def monitor_provider(provider: str) -> dict:
    if provider not in PROVIDERS:
        raise ValueError("unsupported traffic monitor provider")
    return _monitor_provider(provider)


def _monitor_provider(provider: str | None) -> dict:
    zones = [zone for zone in load_zones() if zone.enabled]
    snapshots = []

    for zone in zones:
        sources = []
        provider_items = [provider] if provider else list(PROVIDERS)
        for provider_id in provider_items:
            provider_config = PROVIDERS[provider_id]
            if getattr(zone, provider_config["enabled_field"]):
                sources.append(
                    {
                        "provider": provider_id,
                        "label": provider_config["label"],
                        "status": "planned",
                        "image": None,
                        "summary": provider_config["summary"],
                    }
                )

        snapshots.append(
            {
                "zone_id": zone.id,
                "zone_name": zone.name,
                "region": zone.region,
                "refresh_minutes": zone.refresh_minutes,
                "sources": sources,
                "notes": zone.notes,
            }
        )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "provider": provider,
        "count": len(snapshots),
        "snapshots": snapshots,
        "errors": [],
        "telegram": {
            "status": "planned",
            "summary": "Telegram image delivery will be wired after capture adapters are implemented.",
        },
    }
