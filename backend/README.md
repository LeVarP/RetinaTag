# RetinaTag Backend

FastAPI backend for OCT B-scan labeling. Provides REST API, JWT authentication, image processing, and database management.

## Quick Start

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run dev server (DB tables created automatically on startup)
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

Default admin credentials: `admin` / `admin` (created on first startup if no users exist).

## Project Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI app, startup events, middleware
│   ├── config.py                # Settings (env vars + .env file)
│   ├── api/
│   │   ├── dependencies.py      # Auth dependencies (get_current_user, require_admin)
│   │   └── v1/
│   │       ├── auth.py          # Login, logout, register
│   │       ├── bscans.py        # Label CRUD for B-scans
│   │       ├── scans.py         # Scan listing, B-scan metadata & previews
│   │       ├── stats.py         # Global statistics
│   │       └── users.py         # User settings, password change
│   ├── db/
│   │   ├── database.py          # Async SQLite engine & session factory
│   │   ├── models.py            # SQLAlchemy models (Scan, BScan, User, UserSettings)
│   │   └── schemas.py           # Pydantic request/response schemas
│   └── services/
│       ├── auth_service.py      # JWT creation, password hashing, user lookup
│       ├── bscan_service.py     # B-scan queries
│       ├── labeling_service.py  # Label update logic
│       ├── preview_service.py   # 16-bit → 8-bit image conversion & caching
│       ├── scan_service.py      # Scan queries with stats
│       ├── stats_service.py     # Aggregated statistics
│       └── user_settings_service.py  # Per-user settings CRUD
└── tests/
    ├── conftest.py              # Async fixtures, in-memory SQLite, test client
    ├── test_api/                # Endpoint tests (auth, bscans, scans, stats, users)
    └── test_services/           # Service layer tests (auth, user_settings)
```

## API Endpoints

### Authentication (`/api/v1/auth`)

| Method | Path              | Auth     | Description                 |
|--------|-------------------|----------|-----------------------------|
| POST   | `/auth/login`     | -        | Login, returns httpOnly cookie |
| POST   | `/auth/logout`    | -        | Clear auth cookie           |
| GET    | `/auth/me`        | Required | Get current user info       |
| POST   | `/auth/register`  | Admin    | Create new user             |

### Scans (`/api/v1/scans`)

| Method | Path                                    | Description                      |
|--------|-----------------------------------------|----------------------------------|
| GET    | `/scans`                                | List all scans with stats        |
| GET    | `/scans/{scan_id}/stats`                | Get scan statistics              |
| GET    | `/scans/{scan_id}/bscans/{index}`       | Get B-scan metadata by index     |
| GET    | `/scans/{scan_id}/bscans/{index}/preview` | Get 8-bit preview image (WebP/PNG) |

### B-Scans (`/api/v1/bscans`)

| Method | Path                       | Auth     | Description                    |
|--------|----------------------------|----------|--------------------------------|
| GET    | `/bscans/{bscan_id}`       | -        | Get B-scan by DB id            |
| POST   | `/bscans/{bscan_id}/label` | Required | Set label (1=healthy, 2=unhealthy) |
| DELETE | `/bscans/{bscan_id}/label` | Required | Clear label (set to unlabeled) |

### Users (`/api/v1/users`)

| Method | Path                   | Auth     | Description              |
|--------|------------------------|----------|--------------------------|
| GET    | `/users/me/settings`   | Required | Get user settings        |
| PUT    | `/users/me/settings`   | Required | Update settings (partial)|
| POST   | `/users/me/password`   | Required | Change password          |

### Statistics (`/api/v1/stats`)

| Method | Path              | Description               |
|--------|-------------------|---------------------------|
| GET    | `/stats`          | Global labeling statistics |
| GET    | `/stats/summary`  | Per-scan summaries         |

### System

| Method | Path       | Description       |
|--------|------------|-------------------|
| GET    | `/`        | API info          |
| GET    | `/health`  | Health check      |

## Database

SQLite with async access via aiosqlite. Tables are created automatically on startup (`create_all`), no migrations needed.

### Models

**Scan** — OCT scan container
- `scan_id` (TEXT, PK), `created_at`, `updated_at`

**BScan** — individual B-scan frame
- `id` (INTEGER, PK), `scan_id` (FK → Scan), `bscan_index` (1-based), `path` (UNIQUE), `label` (0=unlabeled, 1=healthy, 2=unhealthy), `updated_at`
- Indexes: `(scan_id, bscan_index)`, `(scan_id, label)`, `(label)`

**User** — application user
- `id` (INTEGER, PK), `username` (UNIQUE), `hashed_password`, `is_active`, `is_admin`, `created_at`, `updated_at`

**UserSettings** — per-user preferences (one-to-one with User)
- `id` (INTEGER, PK), `user_id` (FK → User, UNIQUE), `auto_advance`, `hotkey_healthy`, `hotkey_unhealthy`, `hotkey_next`, `hotkey_prev`, `updated_at`

## Authentication

- JWT tokens stored in httpOnly cookies (not localStorage)
- Passwords hashed with passlib + bcrypt
- Token expiry: 24 hours (configurable via `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`)
- Default admin user seeded on startup if no users exist
- Registration is admin-only (`require_admin` dependency)

## Image Processing

The preview service converts 16-bit medical images to 8-bit for browser display:

1. Load 16-bit source image (TIFF/PNG)
2. Normalize using percentile method (1st–99th percentile by default)
3. Convert to 8-bit and save as WebP/PNG
4. Cache on disk at `data/cache/previews/`

Subsequent requests serve the cached preview directly.

## Configuration

All settings are loaded from environment variables or a `.env` file in the backend directory.

| Variable                          | Default                              | Description                     |
|-----------------------------------|--------------------------------------|---------------------------------|
| `DATABASE_URL`                    | `sqlite+aiosqlite:///./data/database/oct_labeler.db` | Database connection string |
| `DATA_DIR`                        | `./data`                             | Root data directory             |
| `CACHE_DIR`                       | `./data/cache`                       | Preview cache directory         |
| `SCANS_DIR`                       | `./data/scans`                       | Source images directory         |
| `PREVIEW_FORMAT`                  | `webp`                               | Preview format: webp, png, jpeg |
| `PREVIEW_QUALITY`                 | `85`                                 | Lossy format quality (0–100)    |
| `NORMALIZATION_METHOD`            | `percentile`                         | percentile or fixed_window      |
| `PERCENTILE_LOW` / `PERCENTILE_HIGH` | `1.0` / `99.0`                  | Normalization percentile range  |
| `CORS_ORIGINS`                    | `["http://localhost:5173", ...]`     | Allowed CORS origins            |
| `JWT_SECRET_KEY`                  | (change in production!)              | Secret key for JWT signing      |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `1440`                               | Token expiry (minutes)          |
| `DEFAULT_ADMIN_USERNAME`          | `admin`                              | Initial admin username          |
| `DEFAULT_ADMIN_PASSWORD`          | `admin`                              | Initial admin password          |

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/test_api/test_auth.py -v
```

Tests use an in-memory SQLite database and async httpx test client. See `tests/conftest.py` for fixtures.

## Dependencies

| Package            | Purpose                              |
|--------------------|--------------------------------------|
| fastapi 0.109      | Web framework                       |
| uvicorn 0.27       | ASGI server                         |
| sqlalchemy 2.0     | ORM / async database access         |
| aiosqlite 0.19     | Async SQLite driver                 |
| pydantic 2.5       | Data validation & schemas           |
| pydantic-settings   | Settings from env vars             |
| pillow 10.2        | Image loading & conversion          |
| numpy 1.26         | 16-bit image normalization          |
| python-jose 3.3    | JWT token creation & verification   |
| passlib 1.7.4      | Password hashing                    |
| bcrypt 4.0.1       | Bcrypt backend (pinned — 4.1+ breaks passlib) |
| pytest / httpx     | Testing                             |
| black / ruff / mypy | Code quality                       |
