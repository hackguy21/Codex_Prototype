# Project Hormuz

Project Hormuz monitors defined air and maritime zones, especially the Strait of Hormuz. The current milestone is an architecture scaffold: the workspace keeps the existing panel/sidebar CSS style while exposing only two daily monitoring projects.

Detailed FlightRadar24 and MarineTraffic collection logic is intentionally not implemented yet.

## Requirements

- Python 3.11 or newer recommended
- No external Python package required for the current scaffold
- Browser access to `http://127.0.0.1:8000`

## Run

```powershell
cd "C:\Users\hyseong97\Documents\ProjectHormuz"
python .\backend\server.py
```

With the Codex bundled Python runtime:

```powershell
& 'C:\Users\hyseong97\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\backend\server.py
```

## Current UI

The sidebar contains two categories:

- `META PROJECT`
- `Daily Monitor`

`META PROJECT` contains:

- `메타프로젝트 1`: `수집 및 요약 / 전송`
- `메타프로젝트 2`: `기타`

`Daily Monitor` contains:

- `프로젝트 1`: `FlightRadar24`
- `프로젝트 2`: `MarineTraffic`

Only these two monitoring projects are exposed in the current workspace UI and meta-project settings.

## API

- `GET /api/projects`
- `GET /api/meta_project/settings`
- `POST /api/meta_project/settings`
- `POST /api/meta_project/scrape`
- `POST /api/meta_project/scrape-and-send`
- `GET /api/traffic_monitor/zones`
- `POST /api/flightradar24/monitor`
- `POST /api/marine_traffic/monitor`

## Verification

```powershell
& 'C:\Users\hyseong97\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m py_compile .\backend\server.py .\backend\projects\traffic_monitor\service.py .\backend\projects\meta_project\config.py .\backend\projects\meta_project\service.py
node --check .\frontend\app.js
git diff --check
```

## Security

Runtime credentials belong under `data/meta_project/secure/`. That directory is ignored by Git and is not included in this scaffold.
