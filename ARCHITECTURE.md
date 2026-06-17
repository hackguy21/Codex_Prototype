# Architecture

Project Prototype provides a CSS/UI and architecture prototype for vibe-coding workflows. The app is intentionally small so its structure can be copied, extended, or used as a reference when starting a new local project.

## Navigation

```text
META PROJECT
  메타프로젝트 1  전체 요약 및 전송
  메타프로젝트 2  코드구조 및 현재규칙

NORMAL PROJECT
  일반프로젝트 1  example_1
```

`META PROJECT` contains screens that explain, summarize, or manage the prototype itself.

`NORMAL PROJECT` contains ordinary feature projects. New feature work added through vibe-coding or manual implementation should normally appear under this navigation group.

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
    normal_project/
      example_1/  First example ordinary project slot

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
5. Put new ordinary backend feature code under `backend/projects/normal_project/<project_id>/` first.
6. Add ordinary feature projects to the `NORMAL PROJECT` navigation group.
7. Move code out of `normal_project` only when it becomes a stable standalone boundary that deserves a different module layout.

Keep new UI work aligned with the existing sidebar, panel, compact list, and result-output patterns. The point of this repository is to make future experiments feel coherent quickly.

## Normal Project Rule

`backend/projects/normal_project/` is the default backend workspace for ordinary feature implementation.

Use it for specific functions, experiments, adapters, or helper modules added during vibe-coding. Each normal project should live in a clearly named subdirectory such as `backend/projects/normal_project/example_1/`.

The frontend should mirror this distinction:

- `META PROJECT`: management, summary, architecture, and workspace-level screens.
- `NORMAL PROJECT`: ordinary feature projects and user-facing experiments.

Avoid creating new top-level project packages until the feature has a clear, reusable boundary.

## Removed Legacy Scope

This refactor intentionally removes the earlier domain-specific scaffolds:

- no scraper modules
- no Telegram or OpenAI integration
- no scheduled automation loop
- no provider-specific monitor UI
- no traffic zone configuration
- no external provider credentials
