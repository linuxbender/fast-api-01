.PHONY: run dev install install-dev test test-cov lint format fix demo clean setup-ssl help

help:
	@echo "Available commands:"
	@echo "  make setup-ssl    - Generate self-signed SSL certificates for HTTPS"
	@echo "  make run          - Start FastAPI development server on http://localhost:8000"
	@echo "  make dev          - Alias for run"
	@echo "  make run-https    - Start FastAPI server with HTTPS on https://localhost:8000"
	@echo "  make demo         - Run the demo script showcasing CRUD operations"
	@echo "  make test         - Run all tests"
	@echo "  make test-cov     - Run tests with coverage report"
	@echo "  make lint         - Run code linter (ruff)"
	@echo "  make format       - Format code with ruff"
	@echo "  make fix          - Lint with auto-fix and format code"
	@echo "  make install      - Install production dependencies"
	@echo "  make install-dev  - Install all dependencies including dev"
	@echo "  make clean        - Remove cache files and directories"

# Generate self-signed SSL certificates for local development
setup-ssl:
	uv run python setup_dev_env.py

# Start FastAPI development server on port 8000
run:
	uv run uvicorn app.app:app --reload --host 0.0.0.0 --port 8000

# Start FastAPI server with HTTPS support
run-https:
	uv run python run.py --https

# Alternative alias for run
dev: run

# Install production dependencies
install:
	uv sync

# Install all dependencies including dev
install-dev:
	uv sync

# Run all tests
test:
	uv run pytest -v

# Run tests with coverage report
test-cov:
	uv run pytest --cov=src/app --cov-report=html --cov-report=term-missing

# Run linter (ruff)
lint:
	uv run ruff check .

# Format code with ruff
format:
	uv run ruff format .

# Lint with auto-fix, then format code
fix:
	uv run ruff check --fix .
	uv run ruff format .

# Run demo script showcasing CRUD operations
demo:
	uv run demo

# Clean cache files and directories
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/ 2>/dev/null || true
	@echo "✅ Cache cleaned"
