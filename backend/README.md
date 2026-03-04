# RetinaTag Backend

FastAPI backend for OCT B-scan labeling.

## Run Locally

From repository root:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs: `http://localhost:8000/docs`

Notes:
- Default admin (`admin/admin`) is created automatically if users table is empty.
- In Docker deployment, backend is internal-only (not published to host); requests go through frontend nginx at `/api/v1/...`.

## Labeling Logic

- `bscan_index` is normalized to **0-based**.
- `healthy` is tri-state:
  - `1` = healthy
  - `0` = not healthy
  - `null` = not necessarily healthy
- `is_labeled` is computed by marker presence:
  - labeled if any of `healthy/cyst/hard_exudate/srf/ped` is `0` or `1`
  - unlabeled only if all these fields are `null`
- Pathology consistency rule:
  - if any pathology marker is set to `1`, backend sets `healthy=0`
- `DELETE /bscans/{id}/label` clears all label fields:
  - `healthy/cyst/hard_exudate/srf/ped -> null`
  - `is_labeled -> false`
  - `label -> 0`

## API (Prefix: `/api/v1`)

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
| GET | `/scans/{scan_id}/bscans` | - | List all B-scans in scan |
| GET | `/scans/{scan_id}/bscans/{index}` | - | B-scan metadata by 0-based index |
| GET | `/scans/{scan_id}/bscans/{index}/preview` | - | Render cached preview |

### B-scans (`/bscans`)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/bscans/{bscan_id}` | - | Get B-scan by DB id |
| POST | `/bscans/{bscan_id}/health` | Required | Set `healthy` to `0` or `1` |
| POST | `/bscans/{bscan_id}/pathology` | Required | Update pathology markers |
| POST | `/bscans/{bscan_id}/label` | Required | Legacy label API (`1/2`), mapped to `healthy` |
| DELETE | `/bscans/{bscan_id}/label` | Required | Clear all label-related fields |

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
| GET | `/users/me/settings` | Required | Get user hotkey settings |
| PUT | `/users/me/settings` | Required | Update user hotkey settings |
| POST | `/users/me/password` | Required | Change password |

Settings payload fields:
- `auto_advance` (legacy stored field; frontend flow is currently manual navigation)
- `hotkey_healthy`, `hotkey_unhealthy`
- `hotkey_cyst`, `hotkey_hard_exudate`, `hotkey_srf`, `hotkey_ped`
- `hotkey_set_all_pathologies_zero`
- `hotkey_next`, `hotkey_prev`

## Runtime Migrations

On startup, the backend applies lightweight SQLite migrations:
- adds missing columns in `bscans` and `user_settings`
- merges duplicate hard exudate sources (`hard_exudate` + `hard_exudate_alt`) into `hard_exudate`
- backfills `healthy`, `label`, `is_labeled` using current logic
- normalizes B-scan indexes from 1-based to 0-based where needed
- backfills hotkeys defaults, including `hotkey_set_all_pathologies_zero='0'`

## Configuration

Environment variables are defined in `.env` (see `backend/app/config.py`):
- `DATABASE_URL`
- `DATA_DIR`, `CACHE_DIR`
- `PREVIEW_FORMAT`, `PREVIEW_QUALITY`
- `JWT_SECRET_KEY`, `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`
- `DEFAULT_ADMIN_USERNAME`, `DEFAULT_ADMIN_PASSWORD`

## Tests

```bash
pytest backend/tests
```
