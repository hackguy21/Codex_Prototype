# Project Prototype

Project Prototype provides a local CSS/UI and architecture prototype for vibe-coding workflows. It is intentionally small: a static frontend, a Python standard-library HTTP server, and JSON-backed project settings.

## Requirements

- Python 3.11 or newer recommended
- No external Python package required
- Browser access to `http://127.0.0.1:8000` in Default, but Sometimes it needs to be run in adjacent port like 8001 or more

## Run

```powershell
cd "C:\Users\hyseong97\Documents\ProjectPrototype"
python .\backend\server.py
```

With the Codex bundled Python runtime:

```powershell
& 'C:\Users\hyseong97\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\backend\server.py
```

- this runtime in valid only in user 'hyseong97'

## Current UI

The sidebar contains one category:

- `META PROJECT`

`META PROJECT` contains:

- `메타프로젝트 1`: `전체 프로젝트 요약`
- `메타프로젝트 2`: `코드구조 및 현재규칙`
- `메타프로젝트 3`: `수집정보 외부 전송`

## API

- `GET /api/projects`
- `GET /api/meta_project/settings`
- `POST /api/meta_project/settings`

## Verification

```powershell
& 'C:\Users\hyseong97\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m py_compile .\backend\server.py .\backend\projects\meta_project\config.py
node --check .\frontend\app.js
git diff --check
```

## Scope

This repository is a prototype shell, not a production product. It intentionally avoids external services, credentials, browser automation, scraping, deployment configuration, and database migrations.
