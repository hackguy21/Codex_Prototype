# Architecture

Project Hormuz is a local monitoring workspace for air and maritime zones around the Strait of Hormuz. The app uses a static HTML/CSS/JavaScript frontend, a standard-library Python HTTP server, JSON files for local persistence, and a small meta-project control plane.

The current goal is architecture only. FlightRadar24 scraping, MarineTraffic scraping, browser automation, image storage, alerting, and Telegram photo delivery are planned boundaries, not implemented collection details.

## Navigation

The visible navigation is intentionally minimal:

```text
META PROJECT
  메타프로젝트 1  수집 및 요약 / 전송
  메타프로젝트 2  기타

Daily Monitor
  프로젝트 1  FlightRadar24
  프로젝트 2  MarineTraffic
```

The ordinary monitoring project category exposes only `FlightRadar24` and `MarineTraffic`.

## Current Layers

```text
frontend/
  index.html      Two-project monitoring workspace
  styles.css      Shared layout, panel, navigator, list, form, and result styles
  app.js          UI state, API calls, rendering, and interaction handlers

backend/
  server.py       Standard-library HTTP API and static file server
  common/         Shared helpers retained for future use
  projects/
    meta_project/ Workspace project catalog and settings
    traffic_monitor/
      config.py   Zone persistence
      models.py   Zone validation and serialization
      service.py  Provider-specific monitoring snapshot scaffold

data/
  meta_project/       Workspace settings and ignored secure runtime config
  traffic_monitor/    Zone configuration
```

## Project Boundaries

`FlightRadar24` and `MarineTraffic` are represented as separate projects in the meta-project catalog. Both currently use the shared `traffic_monitor` zone configuration and return provider-specific planned snapshots.

`META PROJECT` restores two workspace-level screens:

- `daily_news_manager`: selected project collection, summary formatting, and Telegram text delivery.
- `other_manager`: structural notes for the current workspace.

`backend/projects/traffic_monitor/service.py` exposes:

- `monitor_provider("flightradar24")`
- `monitor_provider("marinetraffic")`
- `monitor_traffic()` for combined internal checks

## Planned Adapter Boundaries

Keep these adapters inside `backend/projects/traffic_monitor/` until another project needs the same capability:

- `flight_adapter.py`: capture or ingest aviation state for a zone.
- `marine_adapter.py`: capture or ingest vessel state for a zone.
- `snapshot_store.py`: persist captured images and metadata for delivery.
- `traffic_analyzer.py`: compare snapshots, flag notable movement, and prepare report text.
- `telegram_sender.py`: send zone images and summaries through existing Telegram configuration.

## API Shape

- `GET /api/traffic_monitor/zones`
- `POST /api/meta_project/scrape`
- `POST /api/meta_project/scrape-and-send`
- `POST /api/flightradar24/monitor`
- `POST /api/marine_traffic/monitor`

API handlers should return JSON, validate user input before saving, and avoid non-standard-library dependencies unless a future implementation explicitly chooses them.

## Non-Scope For This Scaffold

- no FlightRadar24 scraping or browser automation
- no MarineTraffic scraping or browser automation
- no image capture storage
- no Telegram photo delivery
- no alert thresholds or change detection
- no provider credentials or session handling
