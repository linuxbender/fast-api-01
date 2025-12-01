.PHONY: run dev install install-dev test lint format clean

# Start FastAPI development server
run:
	uv run uvicorn fastapi_01.app:app --reload

# Alternative alias for run
dev: run

# Install production dependencies
install:
	uv pip install -e .

# Install all dependencies including dev
install-dev:
	uv pip install -e ".[dev]"

# Run tests
test:
	uv run pytest

# Run tests with coverage
test-cov:
	uv run pytest --cov=fastapi_01 --cov-report=html --cov-report=term

# Run linter
lint:
	uv run ruff check .

# Format code
format:
	uv run ruff format .

# Lint and auto-fix, then format
fix:
	uv run ruff check --fix .
	uv run ruff format .

# Run demo script
demo:
	uv run demo

# Clean cache files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
