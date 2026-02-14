# Makefile for OCT B-Scan Labeler
# Common commands for development, testing, and deployment

.PHONY: help install dev-backend dev-frontend test lint format docker-build docker-up docker-down clean

# Default target: show help
help:
	@echo "OCT B-Scan Labeler - Available Commands"
	@echo "========================================="
	@echo "Setup:"
	@echo "  make install         Install all dependencies (backend + frontend)"
	@echo ""
	@echo "Development:"
	@echo "  make dev-backend     Start backend development server"
	@echo "  make dev-frontend    Start frontend development server"
	@echo ""
	@echo "Testing:"
	@echo "  make test            Run all tests (backend + frontend)"
	@echo "  make test-backend    Run backend tests"
	@echo "  make test-frontend   Run frontend unit tests"
	@echo "  make test-e2e        Run frontend E2E tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint            Lint all code (backend + frontend)"
	@echo "  make format          Format all code (backend + frontend)"
	@echo "  make typecheck       Type check all code"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build    Build Docker images"
	@echo "  make docker-up       Start Docker containers"
	@echo "  make docker-down     Stop Docker containers"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean           Clean build artifacts and caches"

# ===== SETUP =====

install: install-backend install-frontend
	@echo "All dependencies installed!"

install-backend:
	@echo "Installing backend dependencies..."
	cd backend && python -m venv venv && . venv/bin/activate && pip install -r requirements.txt

install-frontend:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# ===== DEVELOPMENT =====

dev-backend:
	@echo "Starting backend development server..."
	cd backend && . venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@echo "Starting frontend development server..."
	cd frontend && npm run dev

# ===== TESTING =====

test: test-backend test-frontend
	@echo "All tests completed!"

test-backend:
	@echo "Running backend tests..."
	cd backend && . venv/bin/activate && pytest

test-frontend:
	@echo "Running frontend unit tests..."
	cd frontend && npm test

test-e2e:
	@echo "Running E2E tests..."
	cd frontend && npm run test:e2e

# ===== CODE QUALITY =====

lint: lint-backend lint-frontend
	@echo "Linting completed!"

lint-backend:
	@echo "Linting backend..."
	cd backend && . venv/bin/activate && black --check app tests && ruff check app tests && mypy app

lint-frontend:
	@echo "Linting frontend..."
	cd frontend && npm run lint && npm run format:check

format: format-backend format-frontend
	@echo "Formatting completed!"

format-backend:
	@echo "Formatting backend..."
	cd backend && . venv/bin/activate && black app tests && ruff check --fix app tests

format-frontend:
	@echo "Formatting frontend..."
	cd frontend && npm run format

typecheck:
	@echo "Type checking..."
	cd backend && . venv/bin/activate && mypy app
	cd frontend && npm run typecheck

# ===== DOCKER =====

docker-build:
	@echo "Building Docker images..."
	docker compose build

docker-up:
	@echo "Starting Docker containers..."
	docker compose up -d
	@echo "Application available at http://localhost"

docker-down:
	@echo "Stopping Docker containers..."
	docker compose down

# ===== UTILITIES =====

clean:
	@echo "Cleaning build artifacts..."
	rm -rf backend/__pycache__ backend/**/__pycache__ backend/.pytest_cache backend/.mypy_cache backend/.ruff_cache backend/htmlcov
	rm -rf frontend/dist frontend/node_modules/.vite frontend/coverage
	rm -rf data/cache/previews/*
	@echo "Clean completed!"
