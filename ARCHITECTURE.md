# Architecture

Project Prototype provides a CSS/UI and architecture prototype for vibe-coding workflows. The app is intentionally small so its structure can be copied, extended, or used as a reference when starting a new local project.

## Navigation

```text
META PROJECT
  메타프로젝트 1  전체 요약 및 전송
  메타프로젝트 2  기타
```

`전체 요약 및 전송` generates a local summary of the prototype and simulates a send flow without contacting an external service.

`기타` documents the visible structure and extension points of the prototype.

## Current Layers

```text
frontend/
  index.html      Static workspace shell and project views
  styles.css      Shared sidebar, panel, list, button, status, and result styles
  app.js          UI state, API calls, rendering, and interaction handlers

backend/
  server.py       Standard-library HTTP API and static file server
  projects/
    meta_project/
      config.py   Project catalog and settings normalization

data/
  meta_project/
    settings.json Persisted project catalog overrides

scripts/
  windows/        Optional local launch helpers
```

## Runtime Shape

The frontend is static and framework-free. It calls a few JSON endpoints and renders the returned data into reusable UI primitives such as panels, lists, status text, textareas, and action buttons.

The backend uses only Python standard-library modules. `backend/server.py` serves frontend files, validates JSON request bodies, and exposes the prototype API.

Project catalog data lives in `backend/projects/meta_project/config.py` and can be persisted through `data/meta_project/settings.json`.

## API Shape

- `GET /api/projects`
- `GET /api/meta_project/settings`
- `POST /api/meta_project/settings`
- `POST /api/prototype/summary`

API handlers should return JSON, keep validation local and explicit, and avoid external dependencies unless the prototype intentionally grows into a product.

## Extension Model

When adding a new prototype module:

1. Add a project entry in `backend/projects/meta_project/config.py`.
2. Persist matching settings in `data/meta_project/settings.json` when needed.
3. Add the visible view in `frontend/index.html`.
4. Add rendering and API behavior in `frontend/app.js`.
5. Add a bounded backend module under `backend/projects/<project_id>/` only when server-side logic is truly needed.

Keep new UI work aligned with the existing sidebar, panel, compact list, and result-output patterns. The point of this repository is to make future experiments feel coherent quickly.

## Removed Legacy Scope

This refactor intentionally removes the earlier domain-specific scaffolds:

- no scraper modules
- no Telegram or OpenAI integration
- no scheduled automation loop
- no provider-specific monitor UI
- no traffic zone configuration
- no external provider credentials
