# RetinaTag Setup Guide

## Prerequisites

- Python 3
- Docker + Docker Compose v2 (`docker compose`)

## 1) Create Database

```bash
python setup/create_db.py
```

By default, this creates `data/database/oct_labeler.db` and seeds it from:
- `backend/app/db/Overview info_all_sheets - Overview info_all_sheets.csv`

Notes:
- `bscan_index` is normalized to **0-based**.
- Duplicate hard exudate columns in CSV are merged (`OR`).
- `healthy` is tri-state (`1/0/null`), `is_labeled` is marker-based.

Useful options:

```bash
# Create DB without CSV seed
python setup/create_db.py --no-seed

# Custom DB file
python setup/create_db.py --output /path/to/oct_labeler.db

# Custom CSV path
python setup/create_db.py --csv /path/to/data.csv
```

## 2) Configure Environment

```bash
cp setup/.env.example .env
```

Required in `.env`:

- `JWT_SECRET_KEY` (generate: `openssl rand -hex 32`)
- `OCT_DATA_PATH` (absolute host path to images)

Example `OCT_DATA_PATH`:
- `/home/user/datasets/oct_images`

Inside container this is mounted to `/mnt/oct-data`.

## 3) Start

```bash
docker compose up --build -d
```

Open:
- Frontend: http://localhost

LAN access:
- Open `http://<HOST_LAN_IP>/` from any device in your local network.
- Find host LAN IP on Linux: `hostname -I` or `ip -4 addr`.

External access:
- Open `http://<HOST_PUBLIC_IP>/` if your network/firewall/router allows inbound TCP `80` to this host.

Login:
- `admin` / `admin` (auto-created if no users exist)

## 4) Verify

```bash
docker compose ps
# frontend health (from host):
curl -I http://localhost/

# backend health (internal, because backend port is not exposed):
docker compose exec -T backend python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health').read().decode())"
```

## Network Access

This setup is configured so that:
- frontend is exposed on port `80`
- backend is **not** exposed to host/network directly
- nginx does not apply source-IP restrictions by default

If you need to limit access, enforce it at firewall/router level or re-add nginx ACL rules.

## 5) Stop

```bash
docker compose down
```

## Schema Highlights

### `bscans`

- `scan_id`, `bscan_index` (0-based), `bscan_key`, `path`
- `cyst`, `hard_exudate`, `srf`, `ped`
- `healthy` (1/0/null)
- `is_labeled`, `label`, `updated_at`

### `user_settings`

- `auto_advance`
- `hotkey_healthy`, `hotkey_unhealthy`
- `hotkey_cyst`, `hotkey_hard_exudate`, `hotkey_srf`, `hotkey_ped`
- `hotkey_next`, `hotkey_prev`
