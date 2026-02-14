# RetinaTag Setup Guide

Three steps: create the database, configure environment, start containers.

## Prerequisites

- Python 3 (any version — the setup script uses only the standard library)
- Docker & Docker Compose

## Step 1: Create the database

```bash
python setup/create_db.py
```

This creates an empty SQLite database at `data/database/oct_labeler.db` with all required tables.

Use `--output` to specify a different path:

```bash
python setup/create_db.py --output /path/to/oct_labeler.db
```

## Step 2: Populate the database

Insert your data into the `scans` and `bscans` tables. The app does **not** prescribe how your images are organized — only that each B-scan row points to a valid image path.

### Schema

**scans** — one row per OCT scan / tomogram:

| Column       | Type     | Description              |
|--------------|----------|--------------------------|
| `scan_id`    | TEXT PK  | Unique scan identifier   |
| `created_at` | DATETIME | Auto-filled              |
| `updated_at` | DATETIME | Auto-filled              |

**bscans** — one row per B-scan frame:

| Column        | Type        | Description                                    |
|---------------|-------------|------------------------------------------------|
| `id`          | INTEGER PK  | Auto-increment                                 |
| `scan_id`     | TEXT FK      | References `scans.scan_id`                    |
| `bscan_index` | INTEGER     | Frame position within the scan (1-based)       |
| `path`        | TEXT UNIQUE | **Absolute path** to the image file            |
| `label`       | INTEGER     | `0` = unlabeled, `1` = healthy, `2` = unhealthy |
| `updated_at`  | DATETIME    | Auto-filled                                    |

> **Important:** the `path` column must contain the path as it will be seen **inside the Docker container**. Since the image directory is mounted at `/mnt/oct-data`, paths should look like `/mnt/oct-data/patient_001/frame_042.png`.

### Example

```sql
-- Insert a scan
INSERT INTO scans (scan_id) VALUES ('PATIENT_001');

-- Insert B-scans (all unlabeled by default)
INSERT INTO bscans (scan_id, bscan_index, path) VALUES
    ('PATIENT_001', 1, '/mnt/oct-data/PATIENT_001/001.png'),
    ('PATIENT_001', 2, '/mnt/oct-data/PATIENT_001/002.png'),
    ('PATIENT_001', 3, '/mnt/oct-data/PATIENT_001/003.png');
```

You can use any tool: `sqlite3` CLI, Python, a custom script, etc.

## Step 3: Configure environment

```bash
cp setup/.env.example .env
```

Open `.env` and set the **required** variables:

| Variable         | What to set                                           |
|------------------|-------------------------------------------------------|
| `JWT_SECRET_KEY` | Random secret — generate with `openssl rand -hex 32`  |
| `OCT_DATA_PATH`  | Absolute path on the **host** to your image directory |

Everything else has working defaults. See `.env.example` for the full list.

## Step 4: Start

```bash
docker-compose up -d
```

Open http://localhost in a browser. Log in with `admin` / `admin` (default credentials, created on first startup).

### Verify

```bash
# Check containers are running
docker-compose ps

# Check backend health
curl http://localhost:8000/health

# View logs
docker-compose logs -f backend
```

## Stopping

```bash
docker-compose down
```

Your database and images are stored outside the containers (in `data/` and the mounted image directory), so nothing is lost.
