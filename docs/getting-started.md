# Getting Started

A quick guide to start developing with FastAPI 01.

## Starting the Project

### Development Server

```bash
make run
```

The server runs at: http://127.0.0.1:8000

### Access API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## Understanding the Project Structure

```
FastAPI_01/
├── src/fastapi_01/          # Main code
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # CLI entry point
│   ├── app.py               # FastAPI application
│   └── Demo.py              # Demo module
├── tests/                   # Test suite
│   ├── conftest.py          # Pytest configuration
│   └── test_app.py          # API tests
├── docs/                    # Documentation
├── pyproject.toml           # Project configuration
├── Makefile                 # Development commands
└── README.md
```

## Creating Your First Endpoint

### 1. Add Endpoint to app.py

```python
@app.get("/hello/{name}")
def say_hello(name: str) -> dict[str, str]:
    """Greet someone by name"""
    return {"message": f"Hello, {name}!"}
```

### 2. Write a Test

Create a test in `tests/test_app.py`:

```python
def test_say_hello(client: TestClient):
    """Test the hello endpoint"""
    response = client.get("/hello/World")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}
```

### 3. Run Tests

```bash
make test
```

### 4. Format Code

```bash
make fix
```

## Development Workflow

### 1. Develop New Features

```bash
# Write tests
# Implement code
# Run tests
make test

# Check and format code
make fix
```

### 2. Server in Watch Mode

The development server (`make run`) automatically detects changes and reloads.

### 3. Ensure Code Quality

```bash
# Linting
make lint

# Formatting
make format

# Or both with auto-fix
make fix
```

## Makefile Commands

| Command | Description |
|---------|-------------|
| `make run` | Start development server |
| `make test` | Run tests |
| `make test-cov` | Run tests with coverage |
| `make lint` | Check code quality |
| `make format` | Format code |
| `make fix` | Auto-fix + format |
| `make install` | Install dependencies |
| `make install-dev` | Install dev dependencies |
| `make demo` | Run demo script |
| `make clean` | Clean cache files |

## Next Steps

- [API Reference](api-reference.md) - All available endpoints
- [Examples](examples.md) - Code examples and patterns
