# OCT B-Scan Labeler

A web application for rapid labeling of OCT (Optical Coherence Tomography) B-scans. Designed for medical researchers who need to quickly classify hundreds of B-scans per tomogram as either Healthy or Unhealthy using keyboard-only navigation.

## Features

- **Keyboard-First Interface**: Navigate and label using only Arrow keys + A/S hotkeys (no mouse required)
- **Smart Preview Caching**: Automatic 16-bit → 8-bit image conversion with disk caching
- **Intelligent Prefetching**: Seamless navigation with automatic prefetch of next K frames
- **Progress Tracking**: Real-time statistics showing labeling progress per scan and globally
- **Two Navigation Modes**: Sequential (all frames) or Unlabeled Only (skip labeled frames)
- **Auto-Advance**: Automatically moves to next frame after labeling
- **Import/Export CLI Tools**: Easy data management with command-line utilities
- **Docker Deployment**: Simple deployment for local, VM, or LAN access

## Architecture

### Technology Stack

- **Backend**: FastAPI + SQLAlchemy + SQLite + Pillow/NumPy
- **Frontend**: React 18 + TypeScript + Vite + TanStack Query
- **Deployment**: Docker + Docker Compose + nginx
- **Testing**: pytest (backend), Vitest + Playwright (frontend)

### Project Structure

```
eye_lableler/
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── api/v1/   # REST endpoints
│   │   ├── db/       # Database models and schemas
│   │   ├── services/ # Business logic
│   │   └── utils/    # Utilities (image processing)
│   ├── tests/        # Backend tests
│   └── scripts/      # Database initialization
├── frontend/         # React + TypeScript application
│   ├── src/
│   │   ├── pages/    # Page components
│   │   ├── components/ # Reusable UI components
│   │   ├── hooks/    # Custom React hooks
│   │   ├── services/ # API client
│   │   ├── styles/   # CSS Modules
│   │   └── types/    # TypeScript types
│   └── tests/        # Frontend tests
├── scripts/          # CLI tools (import/export)
├── docker/           # Docker configuration
└── data/             # Data directory (git-ignored)
    ├── scans/        # Original 16-bit B-scans
    ├── cache/        # Generated 8-bit previews
    └── database/     # SQLite database
```

## Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 20+**
- **Docker & Docker Compose** (for containerized deployment)

### Option 1: Docker Deployment (Recommended)

1. Clone the repository:
```bash
git clone <repo-url>
cd eye_lableler
```

2. Build and start containers:
```bash
make docker-build
make docker-up
```

3. Access the application:
- Frontend: http://localhost
- Backend API: http://localhost/api
- API docs: http://localhost/api/docs

### Option 2: Local Development

1. Install dependencies:
```bash
make install
# This runs:
# - Backend: cd backend && python -m venv venv && pip install -r requirements.txt
# - Frontend: cd frontend && npm install
```

2. Configure environment:
```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env if needed

# Frontend
cp frontend/.env.example frontend/.env
# Edit frontend/.env if needed
```

3. Initialize database:
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python scripts/init_db.py
```

4. Start development servers (in separate terminals):
```bash
# Terminal 1: Backend
make dev-backend

# Terminal 2: Frontend
make dev-frontend
```

5. Access the application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

## Usage

### 1. Import OCT Scans

Use the CLI tool to import B-scans from a directory:

```bash
cd scripts
python import_scan.py --scan-id ABC123 --source /path/to/bscan/images/
```

This will:
- Create a scan record in the database
- Copy images to `data/scans/ABC123/`
- Initialize all B-scans with `label=0` (unlabeled)

### 2. Label B-Scans

1. Open the web interface
2. Select a scan from the list
3. Use keyboard to navigate and label:
   - **Arrow Left**: Previous B-scan
   - **Arrow Right**: Next B-scan
   - **A**: Label as Healthy
   - **S**: Label as Unhealthy
4. After labeling, the app auto-advances to the next frame
5. Toggle between "Sequential" and "Unlabeled Only" modes as needed

### 3. View Statistics

Navigate to the Stats page (`/stats`) to view:
- Global statistics (total scans, B-scans, completion %)
- Per-scan breakdown (labeled counts, progress)
- Label distribution (healthy vs unhealthy)

### 4. Export Labels

Export labels to CSV for analysis:

```bash
cd scripts
python export_labels.py --scan-id ABC123 --output labels.csv
# Or export all:
python export_labels.py --all --output all_labels.csv
```

## API Endpoints

### Scans
- `GET /api/v1/scans` - List all scans with progress
- `GET /api/v1/scans/{scan_id}/stats` - Get scan statistics
- `GET /api/v1/scans/{scan_id}/bscans/{index}` - Get B-scan metadata

### B-Scans
- `POST /api/v1/bscans/{bscan_id}/label` - Update label (body: `{label: 1|2}`)
- `GET /api/v1/scans/{scan_id}/bscans/{index}/preview` - Get 8-bit preview image

### Statistics
- `GET /api/v1/stats` - Get global statistics

Full API documentation available at `/docs` endpoint when server is running.

## Development

### Available Commands

```bash
# Setup
make install         # Install all dependencies

# Development
make dev-backend     # Start backend server
make dev-frontend    # Start frontend server

# Testing
make test            # Run all tests
make test-backend    # Run backend tests only
make test-frontend   # Run frontend unit tests
make test-e2e        # Run E2E tests

# Code Quality
make lint            # Lint all code
make format          # Format all code
make typecheck       # Type check all code

# Docker
make docker-build    # Build Docker images
make docker-up       # Start containers
make docker-down     # Stop containers

# Utilities
make clean           # Clean build artifacts
```

### Testing

**Backend Tests**:
```bash
cd backend
source venv/bin/activate
pytest
pytest --cov=app --cov-report=html  # With coverage
```

**Frontend Tests**:
```bash
cd frontend
npm test              # Unit tests
npm run test:e2e      # E2E tests
```

### Code Quality

**Backend**:
- Formatting: `black app tests`
- Linting: `ruff check app tests`
- Type checking: `mypy app`

**Frontend**:
- Formatting: `npm run format`
- Linting: `npm run lint`
- Type checking: `npm run typecheck`

## Database Schema

### scans
- `scan_id` (TEXT, PRIMARY KEY)
- `created_at` (TEXT)
- `updated_at` (TEXT)

### bscans
- `id` (INTEGER, PRIMARY KEY)
- `scan_id` (TEXT, FOREIGN KEY → scans)
- `bscan_index` (INTEGER)
- `path` (TEXT, UNIQUE)
- `label` (INTEGER) - 0=unlabeled, 1=healthy, 2=unhealthy
- `updated_at` (TEXT)

**Indexes**: `(scan_id, bscan_index)`, `(scan_id, label)`

## Configuration

### Backend Configuration

Edit `backend/.env`:
- `DATABASE_URL`: SQLite database path
- `DATA_DIR`: Root data directory
- `PREVIEW_FORMAT`: Preview image format (webp recommended)
- `NORMALIZATION_METHOD`: percentile or fixed_window
- `CORS_ORIGINS`: Allowed frontend origins

### Frontend Configuration

Edit `frontend/.env`:
- `VITE_API_BASE_URL`: Backend API URL
- `VITE_PREFETCH_COUNT`: Number of frames to prefetch (default: 10)

## Deployment

### Docker Deployment (Production)

1. Build images:
```bash
docker-compose build
```

2. Start services:
```bash
docker-compose up -d
```

3. Import data:
```bash
docker-compose exec backend python /app/scripts/import_scan.py --scan-id ABC123 --source /data/source/
```

### LAN Access

To make the application accessible on your local network:

1. Update `docker-compose.yml` to bind to all interfaces:
```yaml
services:
  frontend:
    ports:
      - "0.0.0.0:80:80"
```

2. Configure firewall (if needed):
```bash
sudo ufw allow from 192.168.1.0/24 to any port 80
```

3. Access from other devices:
```
http://<your-server-ip>
```

## Performance

- **Preview Generation**: <500ms per 16-bit image (first time)
- **Navigation**: <100ms after cache warm-up
- **API Response**: <200ms (p95)
- **Prefetch**: Next 10 frames loaded in background

## Troubleshooting

### Backend Issues

**Database not found**:
```bash
python backend/scripts/init_db.py
```

**Import errors**:
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend Issues

**Dependencies not installed**:
```bash
cd frontend
npm install
```

**API connection refused**:
- Check backend is running on port 8000
- Verify `VITE_API_BASE_URL` in `frontend/.env`

### Docker Issues

**Permission errors**:
```bash
# Ensure data directory has correct permissions
chmod -R 755 data/
```

**Port conflicts**:
- Check if port 80 (frontend) or 8000 (backend) are already in use
- Modify ports in `docker-compose.yml` if needed

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes and test: `make test && make lint`
4. Commit: `git commit -m "Add my feature"`
5. Push: `git push origin feature/my-feature`
6. Create a pull request

### Code Style

- **Python**: Follow PEP 8, use black for formatting
- **TypeScript**: Follow project ESLint rules, use prettier
- **Comments**: All comments in English
- **Docstrings**: Every file starts with a brief description (2-3 lines)
- **React**: NO inline styles, use CSS Modules

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- See [Backend README](backend/README.md) for backend-specific docs
- See [Frontend README](frontend/README.md) for frontend-specific docs
- Check the [implementation plan](.claude/plans/cached-mixing-stardust.md) for architectural details

---

**Built for rapid medical image labeling with efficiency and accuracy in mind.**
