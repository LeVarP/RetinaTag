# OCT B-Scan Labeler - Backend

FastAPI backend for OCT B-scan labeling application. Provides REST API, database management, and image processing services.

## Quick Start

```bash
# Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Initialize database
python scripts/init_db.py

# Run development server
uvicorn app.main:app --reload
```

Access API docs at http://localhost:8000/docs

## Architecture

See [root README](../README.md) for full project documentation.
