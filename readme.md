# RetinaTag

A web application for rapid labeling of OCT (Optical Coherence Tomography) B-scans. Designed for medical researchers who need to quickly classify hundreds of B-scans per tomogram as either Healthy or Unhealthy using keyboard-only navigation.

All code was generated automatically using [Claude Code](https://claude.ai/claude-code) (Anthropic).

## Getting Started

See **[setup/SETUP.md](setup/SETUP.md)** for step-by-step deployment instructions.

## Features

- **Keyboard-First Interface**: Navigate and label using only Arrow keys + A/S hotkeys (no mouse required)
- **Smart Preview Caching**: Automatic 16-bit → 8-bit image conversion with disk caching
- **Intelligent Prefetching**: Seamless navigation with automatic prefetch of next K frames
- **Progress Tracking**: Real-time statistics showing labeling progress per scan and globally
- **Two Navigation Modes**: Sequential (all frames) or Unlabeled Only (skip labeled frames)
- **Auto-Advance**: Automatically moves to next frame after labeling
- **JWT Authentication**: User accounts with per-user customizable hotkeys
- **Docker Deployment**: Single `docker-compose up` for local, VM, or LAN access

## Technology Stack

- **Backend**: FastAPI + SQLAlchemy + SQLite (async) + Pillow/NumPy
- **Frontend**: React 18 + TypeScript + Vite + TanStack Query
- **Deployment**: Docker + Docker Compose + nginx
- **Testing**: pytest (backend), Vitest + Playwright (frontend)

## Project Structure

```
RetinaTag/
├── setup/             # Setup instructions, DB script, env template
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── api/v1/    # REST endpoints (auth, scans, bscans, stats, users)
│   │   ├── db/        # Models, schemas, database config
│   │   └── services/  # Business logic layer
│   └── tests/         # pytest test suite
├── frontend/          # React + TypeScript application
│   ├── src/
│   │   ├── pages/     # ScanList, Labeling, Login, Profile
│   │   ├── components/# BScanViewer, NavigationControls, etc.
│   │   ├── hooks/     # useKeyboardNav, useLabeling, usePrefetch
│   │   ├── context/   # AuthContext, SettingsContext
│   │   └── services/  # API client
│   └── tests/         # Vitest + Playwright tests
├── docker/            # Dockerfiles + nginx config
└── data/              # Runtime data (git-ignored)
    ├── scans/         # Original 16-bit B-scans
    ├── cache/         # Generated 8-bit previews
    └── database/      # SQLite database
```

## API Documentation

Full interactive API docs available at `/docs` when the backend is running.

See [backend/README.md](backend/README.md) for endpoint reference.

## License

MIT
