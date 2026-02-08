# OCT B-Scan Labeler - Backend

FastAPI backend for OCT B-scan labeling application.

## Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── dependencies.py      # Dependency injection
│   ├── api/v1/              # REST API endpoints
│   │   ├── scans.py         # Scan-related endpoints
│   │   ├── bscans.py        # B-scan endpoints (label, preview)
│   │   └── stats.py         # Statistics endpoints
│   ├── db/                  # Database layer
│   │   ├── database.py      # SQLite connection setup
│   │   ├── models.py        # SQLAlchemy ORM models
│   │   └── schemas.py       # Pydantic request/response schemas
│   ├── services/            # Business logic
│   │   ├── scan_service.py
│   │   ├── bscan_service.py
│   │   ├── labeling_service.py
│   │   ├── preview_service.py
│   │   └── stats_service.py
│   └── utils/               # Utilities
│       ├── image_processing.py  # 16→8 bit conversion
│       └── cache.py
├── tests/                   # Test suite
├── scripts/                 # Database initialization scripts
├── requirements.txt         # Python dependencies
├── pytest.ini              # Pytest configuration
├── mypy.ini                # Type checking configuration
└── .env.example            # Environment variables template

## Setup

### 1. Create virtual environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Initialize database

```bash
python scripts/init_db.py
```

### 5. Run development server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at http://localhost:8000
Interactive docs at http://localhost:8000/docs

## API Endpoints

### Scans

- `GET /api/v1/scans` - List all scans with progress
- `GET /api/v1/scans/{scan_id}/stats` - Get scan statistics
- `GET /api/v1/scans/{scan_id}/bscans/{index}` - Get B-scan metadata

### B-Scans

- `POST /api/v1/bscans/{bscan_id}/label` - Update label
- `GET /api/v1/scans/{scan_id}/bscans/{index}/preview` - Get preview image

### Statistics

- `GET /api/v1/stats` - Get global statistics

## Testing

Run all tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=app --cov-report=html
```

View coverage report:

```bash
open htmlcov/index.html
```

## Code Quality

Format code:

```bash
black app tests
```

Lint code:

```bash
ruff check app tests
```

Type check:

```bash
mypy app
```

## Database Schema

### scans

- `scan_id` (TEXT, PRIMARY KEY)
- `created_at` (TEXT)
- `updated_at` (TEXT)

### bscans

- `id` (INTEGER, PRIMARY KEY)
- `scan_id` (TEXT, FOREIGN KEY)
- `bscan_index` (INTEGER)
- `path` (TEXT, UNIQUE)
- `label` (INTEGER) - 0=unlabeled, 1=healthy, 2=unhealthy
- `updated_at` (TEXT)

Indexes: `(scan_id, bscan_index)`, `(scan_id, label)`
