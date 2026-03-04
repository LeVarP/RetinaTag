# RetinaTag Setup Guide

## Prerequisites

- Docker Engine + Docker Compose v2 (`docker compose`)
- Python 3 (needed only if you run `setup/create_db.py` manually)

## 1) Environment

```bash
cp setup/.env.example .env
```

Set required values in `.env`:
- `JWT_SECRET_KEY` (generate: `openssl rand -hex 32`)
- `OCT_DATA_PATH` (absolute host path with OCT images)

Example:
- `OCT_DATA_PATH=/home/user/datasets/oct_images`

This path is mounted into backend container as `/mnt/oct-data` (read-only).

## 2) Optional: Pre-create Database

You can pre-create and seed DB locally:

```bash
python setup/create_db.py
```

Defaults:
- output DB: `data/database/oct_labeler.db`
- seed CSV: `backend/app/db/Overview info_all_sheets - Overview info_all_sheets.csv`

Seed behavior:
- merges duplicate hard exudate columns (`Hard exudate` + `Hard Exudate`) using logical OR
- keeps/normalizes B-scan indexes to 0-based where needed
- derives tri-state `healthy` and marker-based `is_labeled`

Useful options:

```bash
python setup/create_db.py --no-seed
python setup/create_db.py --output /path/to/oct_labeler.db
python setup/create_db.py --csv /path/to/file.csv
```

If you skip this step, backend will still initialize DB tables on first start and seed from default CSV if DB is empty.

## 3) Start Stack

```bash
docker compose up --build -d
```

Open app:
- `http://localhost`

Default login (first start):
- `admin` / `admin`

## 4) Verify

```bash
docker compose ps
curl -I http://localhost/
docker compose exec -T backend python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health').read().decode())"
```

## 5) Access Model

Current docker config:
- frontend is exposed on host port `80`
- backend is internal-only (not published directly)
- nginx does not enforce source-IP ACL by default

So access depends on host/router/firewall rules:
- LAN access: `http://<HOST_LAN_IP>/`
- External access: `http://<HOST_PUBLIC_IP>/` only if inbound `80/tcp` is allowed and routed

To restrict access, configure host firewall/router ACLs (or add nginx IP rules).

## 6) Stop

```bash
docker compose down
```

## Data Model Highlights

### `bscans`

- `scan_id`, `bscan_index` (0-based), `bscan_key`, `path`
- markers: `cyst`, `hard_exudate`, `srf`, `ped`
- health: `healthy` (`1/0/null`)
- status: `is_labeled`, legacy `label`, `updated_at`

Labeled logic:
- labeled if any of `healthy/cyst/hard_exudate/srf/ped` is `0` or `1`
- unlabeled only if all these fields are `null`

### `user_settings`

- `auto_advance` (stored legacy field)
- `hotkey_healthy`, `hotkey_unhealthy`
- `hotkey_cyst`, `hotkey_hard_exudate`, `hotkey_srf`, `hotkey_ped`
- `hotkey_set_all_pathologies_zero`
- `hotkey_next`, `hotkey_prev`

Note:
- On backend startup, lightweight migration adds missing `user_settings` columns automatically (including `hotkey_set_all_pathologies_zero`).
