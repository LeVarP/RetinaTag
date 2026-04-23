# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All common commands are defined in the `Makefile`.

### Development
```bash
make install          # Install all dependencies (backend venv + frontend npm)
make dev-backend      # Start FastAPI dev server (uvicorn, port 8000)
make dev-frontend     # Start Vite dev server (port 5173)
```

### Testing
```bash
make test             # Run all tests
make test-backend     # pytest (backend only)
make test-frontend    # vitest (frontend unit tests only)
make test-e2e         # Playwright E2E tests
```

### Code Quality
```bash
make lint             # black + ruff + mypy (backend), eslint (frontend)
make format           # Auto-format all code
make typecheck        # mypy (backend), tsc (frontend)
```

### Docker Environments
```bash
make prod-up          # Start production (port 80, ./data/)
make prod-rebuild     # Rebuild and restart production
make stage-up         # Start staging (port 8080, ./data-stage/)
make stage-build      # Rebuild and restart staging
```

## Architecture Overview

RetinaTag is a two-tier web app for labeling OCT (Optical Coherence Tomography) B-scan images. The backend exposes a REST API; the frontend is a React SPA served by nginx, which also reverse-proxies `/api/*` to the backend.

```
Browser → nginx (80/8080) → FastAPI (internal :8000) → SQLite + filesystem
```

### Backend (`backend/`)

**FastAPI** with **SQLAlchemy async** (aiosqlite / SQLite). Organized into:

- `app/api/v1/` — HTTP routers (auth, scans, bscans, stats, users)
- `app/services/` — all business logic (auth, scan, bscan, labeling, preview, stats, user_settings)
- `app/db/models.py` — SQLAlchemy ORM models
- `app/db/schemas.py` — Pydantic request/response schemas
- `app/db/database.py` — session factory, `init_db()`, runtime migrations, CSV seeder

**Runtime migrations** run on every startup in `init_db()`: adds missing columns, backfills derived fields (`is_labeled`, `label`), normalizes bscan indexes to 0-based, and seeds from CSV if the DB is empty.

**Preview generation** (`services/preview_service.py`): loads TIFF/PNG from `OCT_DATA_PATH`, normalizes pixel values (percentile or fixed window), renders WebP/PNG/JPEG, caches under `app/data/cache/previews/`.

**Auth**: JWT issued as httpOnly cookie on `POST /api/v1/auth/login`. Protected routes use a FastAPI dependency (`api/dependencies.py`).

### Frontend (`frontend/`)

**React 18 + TypeScript + Vite**. Key patterns:

- `src/services/api.ts` — single Axios instance, all API calls go here; 401 responses emit an `auth:unauthorized` event
- `src/context/` — `AuthContext` (login state) and `SettingsContext` (user hotkeys)
- TanStack React Query for all server state (caching, refetch)
- `src/pages/LabelingPage.tsx` — core labeling UI; keyboard hotkeys wired from user settings

### Key Domain Model

**BScan** is the primary entity. Each has:
- `healthy`: `1` (healthy) | `0` (not healthy) | `null` (not necessarily healthy)
- `cyst`, `hard_exudate`, `srf`, `ped`: each `0` | `1` | `null`
- `is_labeled`: 1 if ANY marker is 0 or 1 (derived, stored)
- `label`: legacy 0/1/2 tri-state derived from `healthy` (0=unlabeled, 1=healthy, 2=unhealthy)

**Pathology consistency rule**: if any pathology marker is set to `1`, `healthy` is auto-set to `0` (enforced in `labeling_service.py`).

### Configuration

Copy `setup/.env.example` to `.env` at the repo root. Required vars:
- `JWT_SECRET_KEY` — generate with `openssl rand -hex 32`
- `OCT_DATA_PATH` — host path to OCT image files

Production and staging share the same OCT image mount (read-only) but have separate databases and caches. Never rebuild prod automatically — it requires `make prod-rebuild` explicitly.

### Default Hotkeys (configurable per user in `/profile`)

| Action | Default |
|--------|---------|
| Healthy | A |
| Not healthy | S |
| Cyst / HE / SRF / PED toggle | 1 / 2 / 3 / 4 |
| Set all pathologies = 0 | 0 |
| Next / Prev B-scan | → / ← |
