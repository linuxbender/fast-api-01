# FastAPI 01

A modern FastAPI project following best practices.

## Features

- ✅ FastAPI Web Framework
- ✅ Modern Python Package Structure (`src/` Layout)
- ✅ UV Package Manager
- ✅ Type Hints
- ✅ Pytest Tests
- ✅ Linting & Formatting with Ruff

## Setup

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) installed

### Installation

1. Clone repository and install dependencies:

```bash
make install
```

Or manually:

```bash
uv pip install -e .
```

## Usage

### Start Development Server

```bash
make run
# or
make dev
```

The server will run at: http://127.0.0.1:8000

### API Documentation

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### Run Demo Script

```bash
make demo
```

### Run Tests

```bash
make test
```

### Format Code

```bash
make format
```

### Linting

```bash
make lint
```

## Project Structure

```
FastAPI_01/
├── src/
│   └── fastapi_01/
│       ├── __init__.py
│       ├── __main__.py
│       ├── app.py          # FastAPI application
│       └── Demo.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_app.py
├── pyproject.toml          # Project configuration
├── Makefile                # Dev commands
└── README.md
```

## Development

### Makefile Commands

- `make run` / `make dev` - Start FastAPI server
- `make demo` - Run demo script
- `make install` - Install dependencies
- `make test` - Run tests
- `make lint` - Code linting
- `make format` - Format code

### Using uv Directly

```bash
# Start server
uv run uvicorn fastapi_01.app:app --reload

# Tests
uv run pytest

# Linting
uv run ruff check .

# Format
uv run ruff format .
```

## License

MIT
