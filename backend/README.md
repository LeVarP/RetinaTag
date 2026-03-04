# RetinaTag Backend

FastAPI backend for OCT B-scan labeling.

## Quick Start

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

Default admin: `admin` / `admin` (seeded automatically if DB has no users).

If you run via the project `docker compose` stack, backend port is intentionally not published to the network. API is reached through frontend nginx proxy (`/api/...`).

## Main Concepts

- `bscan_index` is **0-based**.
- Health is tri-state via `healthy`:
  - `1` = healthy
  - `0` = not healthy
  - `null` = not necessarily healthy
- `is_labeled` is marker-based:
  - labeled if at least one of `healthy/cyst/hard_exudate/srf/ped` is `0` or `1`
  - unlabeled only if all these fields are `null`
- Pathology rule:
  - if any pathology marker becomes `1`, backend auto-sets `healthy=0`.

## API Endpoints

Base prefix: `/api/v1`

### Auth (`/auth`)

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/login` | - | Login, sets httpOnly cookie |
| POST | `/auth/logout` | - | Logout |
| GET | `/auth/me` | Required | Current user |
| POST | `/auth/register` | Admin | Create user |

### Scans (`/scans`)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/scans` | - | List scans with embedded stats |
| GET | `/scans/{scan_id}/stats` | - | Per-scan statistics |
| GET | `/scans/{scan_id}/bscans` | - | List all B-scans for a scan |
| GET | `/scans/{scan_id}/bscans/{index}` | - | B-scan metadata by index |
| GET | `/scans/{scan_id}/bscans/{index}/preview` | - | Render preview image |

### B-scans (`/bscans`)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/bscans/{bscan_id}` | - | Get B-scan by DB id |
| POST | `/bscans/{bscan_id}/health` | Required | Set `healthy` to `0` or `1` |
| POST | `/bscans/{bscan_id}/pathology` | Required | Update pathology markers |
| POST | `/bscans/{bscan_id}/label` | Required | Legacy label API (1/2), mapped to health |
| DELETE | `/bscans/{bscan_id}/label` | Required | Clear health (`healthy=null`) |

### Stats (`/stats`)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/stats` | - | Global statistics |
| GET | `/stats/summary` | - | Per-scan summary |
| GET | `/stats/export/bscans.csv` | Required | Export flat per-B-scan CSV |

CSV export columns:
- `scan_id,bscan_index,bscan_key,healthy,is_labeled,label,cyst,hard_exudate,srf,ped,updated_at`

### Users (`/users`)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/users/me/settings` | Required | Get settings |
| PUT | `/users/me/settings` | Required | Update settings |
| POST | `/users/me/password` | Required | Change password |

Settings fields:
- `auto_advance`
- `hotkey_healthy`, `hotkey_unhealthy`
- `hotkey_cyst`, `hotkey_hard_exudate`, `hotkey_srf`, `hotkey_ped`
- `hotkey_next`, `hotkey_prev`

## Database Model Summary

### `scans`
- `scan_id` (PK)
- `created_at`, `updated_at`

### `bscans`
- `id` (PK)
- `scan_id` (FK), `bscan_index` (0-based), `bscan_key`, `path`
- `cyst`, `hard_exudate`, `srf`, `ped`
- `healthy` (nullable tri-state)
- `is_labeled`, `label`, `updated_at`

### `users`
- `id`, `username`, `hashed_password`, `is_active`, `is_admin`, timestamps

### `user_settings`
- `user_id` (unique FK)
- `auto_advance`
- health hotkeys + pathology hotkeys + navigation hotkeys

## Runtime Migrations

On startup, lightweight SQLite migrations are applied automatically:
- add missing columns
- merge duplicate hard exudate sources from CSV mapping
- normalize `bscan_index` to 0-based where needed
- derive/recompute `healthy`, `label`, `is_labeled`
- add new user pathology hotkey columns with defaults

## Configuration

Environment variables are loaded from `.env` (see `app/config.py`).

Common vars:
- `DATABASE_URL`
- `DATA_DIR`, `CACHE_DIR`
- `PREVIEW_FORMAT`, `PREVIEW_QUALITY`
- `JWT_SECRET_KEY`, `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`
- `DEFAULT_ADMIN_USERNAME`, `DEFAULT_ADMIN_PASSWORD`

## Tests

```bash
pytest
```
