# GitHub Copilot Instructions

## Role

You are a **Professional Python Developer** with expertise in:
- project language: English
- documentation language: English
- Python 3.14 and above
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
- Don't write summary or othr document *.md files in the end of a prompt

## Project Context

This project uses **uv** as the Python package manager and build tool.

## Package Manager

- **Always use `uv` instead of `pip` or `poetry`**
- Dependencies are defined in `pyproject.toml`
- Lock file: `uv.lock`

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
│   └── app/
│       ├── __init__.py
│       ├── __main__.py
│       ├── app.py
│       ├── config/
│       │   ├── correlation_id_middleware.py
│       │   ├── dependencies.py
│       │   ├── exceptions.py
│       │   ├── logger.py
│       │   ├── routes.py
│       │   ├── settings.py
│       │   └── ssl_generator.py
│       ├── controller/
│       │   └── v1/
│       │       ├── base_controller.py
│       │       ├── post_controller.py
│       │       └── dto/
│       │           └── post_dto.py
│       ├── data/
│       │   └── v1/
│       │       ├── base_repository.py
│       │       ├── post_repository.py
│       │       └── model/
│       │           └── post.py
│       ├── service/
│       │   └── v1/
│       │       ├── base_service.py
│       │       └── post_service.py
│       └── security/
│           └── cors_config.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_app.py
│   ├── test_base_repository.py
│   ├── test_base_service.py
│   ├── test_logger.py
│   ├── test_post_controller.py
│   ├── test_routes.py
│   ├── test_settings.py
│   └── __pycache__/
├── docs/
│   └── *.md
├── certs/
├── pyproject.toml
├── uv.lock
├── Makefile
└── README.md
```

## Test Strategy: Focus on Unit Tests

This project **prioritizes Unit Tests** for isolated business logic testing.

### Unit Tests (Primary Focus)
**Definition**: Test a single function, method, or class in isolation, mocking all external dependencies.

**Characteristics**:
- Fast execution (milliseconds)
- No database, no external services
- Mock all dependencies using `unittest.mock`, `pytest-mock`, or `mocker` fixture
- Test business logic in isolation
- Test edge cases and error conditions
- High code coverage (>80%)

**When to write Unit Tests**:
- Service layer methods (business logic)
- Repository methods (data access logic)
- Utility functions and helpers
- Validators and formatters
- Exception handling

**Example - Unit Test for Service**:
```python
def test_post_service_create_returns_dto_with_id(mocker):
    """Test PostService.create business logic only."""
    # Arrange - Mock the repository
    mock_repo = mocker.Mock()
    mock_repo.add.return_value = Post(id=1, title="Test", content="Content", author="John")
    
    service = PostService(mock_repo)
    dto = PostDto(title="Test", content="Content", author="John")
    
    # Act
    result = service.create(dto)
    
    # Assert
    assert result.id == 1
    assert result.title == "Test"
    mock_repo.add.assert_called_once()
```

**Example - Unit Test for Repository**:
```python
def test_post_repository_get_all_returns_all_posts(mocker):
    """Test PostRepository.get_all returns all posts from database."""
    # Arrange - Mock the session
    mock_session = mocker.Mock()
    mock_session.query().all.return_value = [
        Post(id=1, title="Post 1"),
        Post(id=2, title="Post 2"),
    ]
    
    repository = PostRepository(mock_session)
    
    # Act
    results = repository.get_all()
    
    # Assert
    assert len(results) == 2
    assert results[0].id == 1
```

### Mocking Strategy
- **Use `pytest-mock` or `mocker` fixture** for dependency injection
- **Mock database sessions** to avoid real DB calls
- **Mock external services** (APIs, cache, etc.)
- **Verify mock calls** with `assert_called()`, `assert_called_once()`, `assert_called_with()`

### Project Test Structure
- **All tests are Unit Tests** with mocked dependencies
- **Unit Tests**: `test_base_service.py`, `test_base_repository.py`, `test_post_controller.py`, etc.
- **Configuration Tests**: `test_settings.py`, `test_logger.py`
- **Goal**: High test coverage (>80%) with fast, isolated tests

## Python Version

- This project uses **Python 3.14**
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

