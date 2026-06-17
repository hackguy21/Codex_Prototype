# Architecture

Project Prototype provides a CSS/UI and architecture prototype for vibe-coding workflows. It keeps a small local web application structure that can be copied, extended, or used as a reference when starting a new project.

The current goal is not a finished domain product. The repository demonstrates a working local frontend, a standard-library Python HTTP server, JSON-backed settings, and a meta-project control plane that shows how future projects can be organized.

## Navigation

The visible navigation is intentionally minimal:

```text
META PROJECT
  메타프로젝트 1  Project Prototype
  메타프로젝트 2  기타

Daily Monitor
  프로젝트 1  FlightRadar24
```

`Project Prototype` is the primary meta-project screen. It describes the purpose of the workspace: providing CSS/UI and architecture patterns for vibe-coding.

`기타` is the structural reference screen. It summarizes the folders, current capabilities, and extension points of this prototype.

`FlightRadar24` remains as a sample ordinary project. It is kept as a scaffolded example of how a domain-specific project can plug into the shared UI and API shape.

## Current Layers

```text
frontend/
  index.html      Static workspace shell and project views
  styles.css      Shared sidebar, panel, list, button, status, and result styles
  app.js          UI state, API calls, rendering, and interaction handlers

backend/
  server.py       Standard-library HTTP API and static file server
  common/         Shared helpers retained for future project modules
  projects/
    meta_project/ Project catalog, settings normalization, and orchestration
    traffic_monitor/
      config.py   Sample zone persistence
      models.py   Sample data validation and serialization
      service.py  Sample provider response scaffold

data/
  meta_project/       Workspace settings and ignored secure runtime config
  traffic_monitor/    Sample project data

scripts/
  windows/            Local launch helpers
```

## Prototype Boundaries

The repository is organized around repeatable application shape rather than a single finished feature:

- `frontend/index.html` defines the first-pass workspace layout and project panels.
- `frontend/styles.css` is the main CSS/UI reference for future vibe-coded screens.
- `frontend/app.js` demonstrates lightweight state management, API calls, rendering, copy actions, and panel toggles without a frontend framework.
- `backend/server.py` serves static files and exposes JSON endpoints using only Python standard-library modules.
- `backend/projects/meta_project/` keeps the catalog of visible projects and normalizes persisted settings.
- `data/meta_project/settings.json` stores the current project list and selected project state.

The remaining `traffic_monitor` and `FlightRadar24` pieces are sample modules. They show how a real project can attach to the same structure, but they are not the core purpose of Project Prototype.

## API Shape

Current API endpoints include:

- `GET /api/projects`
- `GET /api/meta_project/settings`
- `POST /api/meta_project/settings`
- `GET /api/traffic_monitor/zones`
- `POST /api/flightradar24/monitor`

Legacy or scaffold endpoints may still exist while the prototype is being simplified. New work should prefer endpoints that match the visible Project Prototype navigation and avoid adding domain-specific behavior unless the project intentionally grows in that direction.

## Extension Model

When adding a new prototype project:

1. Add a project entry in `backend/projects/meta_project/config.py`.
2. Persist matching settings in `data/meta_project/settings.json` when needed.
3. Add the visible view in `frontend/index.html`.
4. Add rendering and API behavior in `frontend/app.js`.
5. Add a bounded backend module under `backend/projects/<project_id>/` only when the project needs server-side logic.

Keep new UI work aligned with the existing sidebar, panel, compact list, and result-output patterns. The point of this repository is to make future experiments feel coherent quickly.

## Non-Scope For This Prototype

- no production authentication
- no database migration layer
- no deployment pipeline
- no frontend framework build system
- no real browser automation or capture pipeline
- no provider credentials or session handling
- no finished domain-specific monitoring product
