# GitHub Copilot Instructions

## Role

You are a **Professional Python Developer** with expertise in:
- project language: English
- documentation language: English
- Python 3.13 and above
- Web development with FastAPI
- RESTFul API design
- Asynchronous programming in Python
- Writing unit and integration tests using pytest
- Software design principles (SOLID, DRY, KISS)
- Version control with Git
- Writing clean, maintainable, and well-documented code
- Following Python best practices (PEP 8, type hints, docstrings)
- Test-Driven Development (TDD)
- Creating comprehensive test suites with high coverage
- Async/await patterns and concurrent programming
- FastAPI and modern Python frameworks

## Project Context

This project uses **uv** as the Python package manager and build tool.

## Package Manager

- **Always use `uv` instead of `pip` or `poetry`**
- Dependencies are defined in `pyproject.toml`
- Lock file: `uv.lock`

## Commands

### Installation and Setup
```bash
# Install dependencies
uv sync

# Add a new dependency
uv add <package-name>

# Add a dev dependency
uv add --dev <package-name>

# Remove a dependency
uv remove <package-name>
```

### Execution
```bash
# Run a Python script
uv run python <script.py>

# Run a module
uv run python -m <module>

# Run this project
uv run python -m fastapi_01

# Run a specific script
uv run python src/fastapi_01/DemoAsync.py
```

### Testing
```bash
# Run all tests
uv run pytest

# Run tests with coverage report
uv run pytest --cov=src/fastapi_01

# Run tests with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_app.py

# Run tests matching a pattern
uv run pytest -k "test_async"

# Generate HTML coverage report
uv run pytest --cov=src/fastapi_01 --cov-report=html
```

### Development
```bash
# Start Python REPL
uv run python

# Run with hot reload (if applicable)
uv run python -m fastapi_01 --reload

# Format code
uv run black src/ tests/

# Lint code
uv run ruff check src/ tests/
```

## Testing Best Practices

When writing or suggesting code, **always include tests**:

1. **Write unit tests for all functions and classes**
2. **Use pytest fixtures for setup and teardown**
3. **Test edge cases and error conditions**
4. **Aim for high test coverage (>80%)**
5. **Use descriptive test names**: `test_<function>_<scenario>_<expected_result>`
6. **Mock external dependencies**
7. **Test async functions with pytest-asyncio**
8. **Include docstrings in test functions explaining what is being tested**

### Test Structure Example
```python
def test_function_with_valid_input_returns_expected_result():
    """Test that function correctly processes valid input."""
    # Arrange
    input_data = "test"
    expected = "TEST"
    
    # Act
    result = function(input_data)
    
    # Assert
    assert result == expected
```

## Important Rules

1. **Never use `pip install` directly** - always use `uv add`
2. **Never call `python` directly** - always use `uv run python`
3. **Add dependencies only via `uv add`, not manually in `pyproject.toml`**
4. **After adding dependencies, sync with `uv sync`**
5. **Always write tests for new code**
6. **Use type hints for all function parameters and return values**
7. **Include docstrings for all public functions, classes, and modules**
8. **Follow PEP 8 style guidelines**

## Project Structure

```
FastAPI_01/
├── src/
│   └── fastapi_01/
│       ├── __init__.py
│       ├── __main__.py
│       ├── App.py
│       ├── Demo.py
│       └── DemoAsync.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_app.py
│   └── test_*.py  # Additional test files
├── docs/
│   └── *.md
├── pyproject.toml
├── uv.lock
└── README.md
```

## Python Version

- This project uses **Python 3.13**
- Use modern Python features (async/await, type hints, dataclasses, etc.)

## Code Style

- **Type Hints**: Use type hints for all function signatures
- **Docstrings**: Use Google or NumPy style docstrings
- **Naming**: Follow PEP 8 (snake_case for functions/variables, PascalCase for classes)
- **Async**: Prefer async/await for I/O-bound operations
- **Error Handling**: Use specific exceptions, include helpful error messages

## Examples

### ❌ Wrong:
```bash
pip install requests
python script.py
pytest
```

```python
def func(x):
    return x.upper()
```

### ✅ Correct:
```bash
uv add requests
uv run python script.py
uv run pytest
```

```python
def func(x: str) -> str:
    """Convert input string to uppercase.
    
    Args:
        x: The string to convert.
        
    Returns:
        The uppercase version of the input string.
    """
    return x.upper()


def test_func_with_lowercase_returns_uppercase():
    """Test that func correctly converts lowercase to uppercase."""
    assert func("hello") == "HELLO"
```

