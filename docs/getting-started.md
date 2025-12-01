# Getting Started

Ein schneller Einstieg in die Entwicklung mit FastAPI 01.

## Projekt starten

### Development Server

```bash
make run
```

Der Server läuft auf: http://127.0.0.1:8000

### API Dokumentation aufrufen

FastAPI generiert automatisch interaktive API-Dokumentation:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## Projektstruktur verstehen

```
FastAPI_01/
├── src/fastapi_01/          # Hauptcode
│   ├── __init__.py          # Package Initialisierung
│   ├── __main__.py          # CLI Entry Point
│   ├── app.py               # FastAPI Application
│   └── Demo.py              # Demo Module
├── tests/                   # Test Suite
│   ├── conftest.py          # Pytest Configuration
│   └── test_app.py          # API Tests
├── docs/                    # Dokumentation
├── pyproject.toml           # Projekt Configuration
├── Makefile                 # Development Commands
└── README.md
```

## Ersten Endpoint erstellen

### 1. Endpoint in app.py hinzufügen

```python
@app.get("/hello/{name}")
def say_hello(name: str) -> dict[str, str]:
    """Greet someone by name"""
    return {"message": f"Hello, {name}!"}
```

### 2. Test schreiben

Erstelle einen Test in `tests/test_app.py`:

```python
def test_say_hello(client: TestClient):
    """Test the hello endpoint"""
    response = client.get("/hello/World")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}
```

### 3. Tests ausführen

```bash
make test
```

### 4. Code formatieren

```bash
make fix
```

## Development Workflow

### 1. Neue Features entwickeln

```bash
# Tests schreiben
# Code implementieren
# Tests ausführen
make test

# Code prüfen und formatieren
make fix
```

### 2. Server im Watch-Mode

Der Development Server (`make run`) erkennt automatisch Änderungen und lädt neu.

### 3. Code Quality sicherstellen

```bash
# Linting
make lint

# Formatierung
make format

# Oder beides mit Auto-Fix
make fix
```

## Makefile Commands

| Command | Beschreibung |
|---------|-------------|
| `make run` | Start Development Server |
| `make test` | Run Tests |
| `make test-cov` | Run Tests with Coverage |
| `make lint` | Check Code Quality |
| `make format` | Format Code |
| `make fix` | Auto-fix + Format |
| `make install` | Install Dependencies |
| `make install-dev` | Install Dev Dependencies |
| `make demo` | Run Demo Script |
| `make clean` | Clean Cache Files |

## Nächste Schritte

- [API Reference](api-reference.md) - Alle verfügbaren Endpoints
- [Examples](examples.md) - Code-Beispiele und Patterns
