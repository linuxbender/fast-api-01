# FastAPI 01

Ein modernes FastAPI-Projekt mit Best Practices.

## Features

- ✅ FastAPI Web Framework
- ✅ Modern Python Package Structure (`src/` Layout)
- ✅ UV Package Manager
- ✅ Type Hints
- ✅ Pytest Tests
- ✅ Linting & Formatting mit Ruff

## Setup

### Voraussetzungen

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) installiert

### Installation

1. Repository klonen und Dependencies installieren:

```bash
make install
```

Oder manuell:

```bash
uv pip install -e .
```

## Verwendung

### Development Server starten

```bash
make run
# oder
make dev
```

Der Server läuft dann auf: http://127.0.0.1:8000

### API Dokumentation

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### Demo Script ausführen

```bash
make demo
```

### Tests ausführen

```bash
make test
```

### Code formatieren

```bash
make format
```

### Linting

```bash
make lint
```

## Projektstruktur

```
FastAPI_01/
├── src/
│   └── fastapi_01/
│       ├── __init__.py
│       ├── __main__.py
│       ├── app.py          # FastAPI Anwendung
│       └── Demo.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_app.py
├── pyproject.toml          # Projekt-Konfiguration
├── Makefile                # Dev-Commands
└── README.md
```

## Development

### Makefile Commands

- `make run` / `make dev` - FastAPI Server starten
- `make demo` - Demo Script ausführen
- `make install` - Dependencies installieren
- `make test` - Tests ausführen
- `make lint` - Code Linting
- `make format` - Code formatieren

### Mit uv direkt

```bash
# Server starten
uv run uvicorn fastapi_01.app:app --reload

# Tests
uv run pytest

# Linting
uv run ruff check .

# Formatieren
uv run ruff format .
```

## License

MIT
