# Project Prototype

Project Prototype provides a local CSS/UI and architecture prototype for vibe-coding workflows. It is intentionally small: a static frontend, a Python standard-library HTTP server, and JSON-backed project settings.

## Requirements

- Python 3.11 or newer
- A local virtual environment in `.venv` is recommended for all future modules
- No external Python package required yet; add shared runtime packages to `requirements.txt`
- Browser access to `http://127.0.0.1:8000` in Default, but Sometimes it needs to be run in adjacent port like 8001 or more

## Virtual Environment

Create or refresh the local virtual environment:

```powershell
cd "C:\Users\hyseong97\Documents\ProjectPrototype"
.\scripts\windows\setup_venv.ps1
```

The setup script:

- finds Python 3.11 or newer
- creates `.venv` when it does not exist
- upgrades `pip`
- installs packages from `requirements.txt`

If Python 3.11+ is not on `PATH`, point the setup script at a specific interpreter:

```powershell
$env:PROJECT_PROTOTYPE_PYTHON = "C:\Path\To\Python311\python.exe"
.\scripts\windows\setup_venv.ps1
```

Use the virtual environment directly when adding future modules:

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
.\.venv\Scripts\python.exe .\backend\server.py
```

## Run

```powershell
cd "C:\Users\hyseong97\Documents\ProjectPrototype"
.\scripts\windows\run_project_prototype.ps1
```

Without the helper script:

```powershell
.\.venv\Scripts\python.exe .\backend\server.py
```

If `.venv` has not been created yet, the run helper falls back to `python`.

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
.\.venv\Scripts\python.exe -m py_compile .\backend\server.py .\backend\projects\meta_project\config.py
node --check .\frontend\app.js
git diff --check
```

## Scope

This repository is a prototype shell, not a production product. It intentionally avoids external services, credentials, browser automation, scraping, deployment configuration, and database migrations.
