# Architecture

Project Prototype provides a CSS/UI and architecture prototype for vibe-coding workflows. The app is intentionally small so its structure can be copied, extended, or used as a reference when starting a new local project.

## Navigation

```text
META PROJECT
  메타프로젝트 1  전체 프로젝트 요약
  메타프로젝트 2  코드구조 및 현재규칙
  메타프로젝트 3  수집정보 외부 전송

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

## Frontend Composition Rule

Frontend work should be organized from large placement units to smaller functional units.

Each project view should first be divided into independent panels. A panel is the primary layout boundary for a screen and should be labeled in order, such as `# 패널 1`, `# 패널 2`, and `# 패널 3`. The panel number belongs on the first title line so that a developer can refer to a stable screen location during vibe-coding.

Inside each panel, create separate bounded feature boxes for the actual functions or information groups. These boxes should be titled in order, such as `## 기능 1`, `## 기능 2`, and `## 기능 3`, followed by the feature name or role. This makes it easy to say where a new control, API result, form, list, or output area should be placed without depending on visual guesses.

Use this hierarchy when adding or revising frontend UI:

```text
# 패널 1
  ## 기능 1  Main input, location guide, or summary group
  ## 기능 2  Related control, detail, or secondary information

# 패널 2
  ## 기능 1  Status, result, preview, or output group
  ## 기능 2  Follow-up action or log group

# 패널 3
  ## 기능 1  Notes, next steps, or extension guide
```

Panel boundaries should remain broad and stable. Feature boxes can be added, removed, or reordered inside a panel as the prototype evolves, but avoid mixing unrelated functions directly in the panel body without a bounded feature box.

## API Shape

- `GET /api/projects`
- `GET /api/meta_project/settings`
- `POST /api/meta_project/settings`

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

