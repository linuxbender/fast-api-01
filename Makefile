.PHONY: run dev install install-dev test test-cov lint format fix clean env-dev env-staging env-prod help

help:
	@echo "🚀 FastAPI Development Commands"
	@echo ""
	@echo "Server (HTTPS is always enabled):"
	@echo "  make run              - Start FastAPI development server on https://localhost:8000"
	@echo "  make dev              - Alias for run"
	@echo "  make env-dev          - Switch to development environment (.env.development)"
	@echo "  make env-staging      - Switch to staging environment (.env.staging)"
	@echo "  make env-prod         - Switch to production environment (.env.production)"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test             - Run all tests (155 tests)"
	@echo "  make test-cov         - Run tests with coverage report"
	@echo "  make lint             - Run code linter (ruff)"
	@echo "  make format           - Auto-fix linting issues"
	@echo "  make fix              - Fix and check code style"
	@echo ""
	@echo "Setup & Utilities:"
	@echo "  make install          - Install dependencies"
	@echo "  make install-dev      - Install dependencies including dev tools"
	@echo "  make clean            - Remove cache and build artifacts"

# ================================
# Server Management (HTTPS Required)
# ================================

# Start FastAPI development server with HTTPS
# SSL certificates are auto-generated if missing
run:
	uv run python -m app

# Alternative alias for run
dev: run

# ================================
# Environment Configuration
# ================================

# Switch to development environment
env-dev:
	@echo "📝 Switching to development environment..."
	cp .env.development .env
	@echo "✅ Using .env.development (DEBUG, SQLite, HTTPS)"

# Switch to staging environment
env-staging:
	@echo "📝 Switching to staging environment..."
	cp .env.staging .env
	@echo "✅ Using .env.staging (INFO logging, PostgreSQL, HTTPS)"
	@echo "⚠️  Remember to add real certificates from CA"

# Switch to production environment
env-prod:
	@echo "📝 Switching to production environment..."
	cp .env.production .env
	@echo "✅ Using .env.production (WARNING logging, PostgreSQL, HTTPS)"
	@echo "⚠️  Remember to add real certificates from CA"

# ================================
# Installation & Dependencies
# ================================

# Install production dependencies
install:
	uv sync

# Install all dependencies including dev
install-dev:
	uv sync

# ================================
# Testing & Quality Assurance
# ================================

# Run all tests
test:
	uv run pytest -v

# Run tests with coverage report
test-cov:
	uv run pytest --cov=app --cov-report=html --cov-report=term-missing

# Run linter (ruff)
lint:
	uv run ruff check .

# Auto-fix linting issues
format:
	uv run ruff check --fix .

# Fix and check code style
fix:
	uv run ruff check --fix .

# ================================
# Utilities
# ================================

# Clean cache files and directories
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/ 2>/dev/null || true
	@echo "✅ Cache cleaned"
