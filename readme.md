# RetinaTag

RetinaTag is a web app for fast labeling of OCT B-scans with keyboard-friendly controls, pathology markers, and per-scan progress tracking.

## Quick Start

Use the full setup guide: **[setup/SETUP.md](setup/SETUP.md)**.

Minimal Docker start:

```bash
cp setup/.env.example .env
# set OCT_DATA_PATH and JWT_SECRET_KEY in .env
docker compose up --build -d
```

Open: `http://localhost`  
Default login (first run): `admin` / `admin`

## What It Does

- Labels each B-scan with tri-state health:
  - `healthy=1` -> Healthy
  - `healthy=0` -> Not healthy
  - `healthy=null` -> Not necessarily healthy
- Tracks pathology markers per B-scan:
  - `Cyst`, `Hard exudate`, `SRF`, `PED`
- Uses marker-based labeled state:
  - labeled if any of `healthy/cyst/hard_exudate/srf/ped` is `0` or `1`
  - unlabeled only if all those fields are `null`
- Enforces pathology rule:
  - any pathology marker `=1` automatically sets `healthy=0`
- Supports quick actions in labeling UI:
  - `Unlabel` (clear health + all pathology markers to `null`)
  - `Set all pathologies = 0` (without setting Healthy=1)
- Supports configurable user hotkeys in profile, including default `0` for `Set all pathologies = 0`
- Provides scan dashboard with:
  - sortable columns
  - column visibility toggles
  - sticky `Progress` and `Action` columns
  - expandable B-scan details table
  - CSV export (`/stats/export/bscans.csv`, no `path` column)

## Stack

- Backend: FastAPI, SQLAlchemy (async), SQLite, Pillow/NumPy
- Frontend: React 18, TypeScript, Vite, TanStack Query
- Deployment: Docker Compose + nginx

## Repository Map

```text
RetinaTag/
├── setup/      # setup docs, env template, DB creation script
├── backend/    # FastAPI app + tests
├── frontend/   # React app + tests
├── docker/     # Dockerfiles + nginx config
└── data/       # runtime DB/cache (gitignored)
```

## More Docs

- Backend details and API: [backend/README.md](backend/README.md)
- Frontend details and hotkeys: [frontend/README.md](frontend/README.md)
- Setup and deployment: [setup/SETUP.md](setup/SETUP.md)
- Development workflow: [CONTRIBUTING.md](CONTRIBUTING.md)
