# FastAPI 01

A modern, production-ready FastAPI project with generic CRUD operations, centralized routing, global logging with correlation IDs, and HTTPS support for local development.

## ✨ Features

### Core Framework
- ✅ **FastAPI** - Modern, fast web framework
- ✅ **SQLModel** - Type-safe ORM combining SQLAlchemy + Pydantic
- ✅ **Pydantic v2** - Data validation with type hints
- ✅ **Uvicorn** - ASGI server with SSL/HTTPS support

### Architecture & Patterns
- ✅ **Generic Repository Pattern** - `BaseRepository[T]` for reusable CRUD operations
- ✅ **Service Layer** - `BaseService[T, D]` with DTO mapping
- ✅ **Controller Layer** - `BaseController[T, D]` with HTTP routing
- ✅ **Centralized Route Configuration** - Single source of truth for endpoints
- ✅ **Dependency Injection** - Clean service and repository injection

### Development & Operations
- ✅ **Global Logging** - Structured logging with correlation IDs
- ✅ **Request Tracking** - Automatic correlation ID tracking across async contexts
- ✅ **Self-Signed SSL Certificates** - HTTPS for local development
- ✅ **Environment Configuration** - .env based settings management
- ✅ **CORS Support** - Configurable CORS middleware

### Testing & Quality
- ✅ **Comprehensive Test Suite** - 110+ tests with 100% pass rate
- ✅ **pytest** - Modern testing framework
- ✅ **Type Hints** - Full type coverage
- ✅ **Ruff** - Fast linting and formatting
- ✅ **High Coverage** - Config, CRUD, Logging, Routing modules

## Quick Start

### Prerequisites

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. Clone repository:
```bash
git clone <repository>
cd FastAPI_01
```

2. Install dependencies:
```bash
make install
# or
uv sync
```

3. Setup development environment (SSL certificates, .env):
```bash
make setup-ssl
```

## Running the Application

### HTTP (Default)

```bash
make run
# or
uv run python run.py
```

→ http://localhost:8000

### HTTPS (with Self-Signed Certificate)

```bash
make run-https
# or
uv run python run.py --https
```

→ https://localhost:8000  
(Browser will warn about self-signed certificate - this is normal for development)

### Custom Configuration

```bash
# Custom port
uv run python run.py --port 9000

# Custom host
uv run python run.py --host 127.0.0.1

# Without auto-reload
uv run python run.py --no-reload

# Multiple workers
uv run python run.py --workers 4
```

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Testing

Comprehensive test suite with **110 tests** (100% pass rate):

```bash
# Run all tests
make test-all
# or
uv run pytest -v

# Run with coverage report
make test-coverage
# or
uv run pytest --cov=src/app --cov-report=html --cov-report=term

# Run specific test file
uv run pytest tests/test_base_repository.py -v

# Run tests matching pattern
uv run pytest -k "test_crud" -v
```

### Test Files

| File | Tests | Coverage |
|------|-------|----------|
| `test_base_repository.py` | 9 | CRUD operations |
| `test_base_service.py` | 8 | Service layer & DTO mapping |
| `test_settings.py` | 21 | Configuration & environment |
| `test_routes.py` | 39 | Route configuration system |
| `test_logger.py` | 25 | Logging & correlation IDs |
| **Total** | **110** | **100% passing** |

## Development Commands

All commands are available via Makefile or uv directly:

### Server Management

```bash
make run              # Start development server (HTTP)
make run-https        # Start with HTTPS (requires setup-ssl)
make setup-ssl        # Generate self-signed certificates
```

### Testing

```bash
make test             # Run tests quickly
make test-all         # Run all tests with output
make test-coverage    # Generate coverage report
```

### Code Quality

```bash
make lint             # Check code style
make format           # Auto-format code
make format-check     # Check formatting without changing
```

### Demo & Scripts

```bash
make demo             # Run all CRUD operations
make install          # Install dependencies
make clean            # Clean cache & artifacts
```

## Project Structure

```
FastAPI_01/
├── src/app/
│   ├── __init__.py
│   ├── __main__.py              # Demo script entry point
│   ├── app.py                   # FastAPI application
│   │
│   ├── config/                  # Configuration & Settings
│   │   ├── settings.py          # Environment configuration (Pydantic)
│   │   ├── routes.py            # Centralized route configuration
│   │   ├── logger.py            # Global logging with correlation IDs
│   │   ├── ssl_generator.py     # SSL certificate generator
│   │   ├── correlation_id_middleware.py  # Request tracking middleware
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   ├── exceptions.py
│   │   └── logger_examples.py
│   │
│   ├── controller/              # HTTP Controllers (Routes)
│   │   └── v1/
│   │       ├── base_controller.py  # Generic controller base class
│   │       ├── post_controller.py  # Post CRUD endpoints
│   │       └── dto/
│   │           ├── post_dto.py     # Post Data Transfer Object
│   │
│   ├── service/                 # Business Logic Layer
│   │   └── v1/
│   │       ├── base_service.py  # Generic service with DTO mapping
│   │       └── post_service.py  # Post business logic
│   │
│   ├── data/                    # Data Access Layer
│   │   ├── database.py
│   │   └── v1/
│   │       ├── base_repository.py  # Generic repository (CRUD)
│   │       ├── post_repository.py  # Post data access
│   │       └── model/
│   │           └── post.py         # SQLModel entity
│   │
│   └── security/
│       └── cors_config.py       # CORS configuration
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # pytest configuration
│   ├── test_base_repository.py  # CRUD operations tests
│   ├── test_base_service.py     # Service layer tests
│   ├── test_settings.py         # Configuration tests
│   ├── test_routes.py           # Route configuration tests
│   └── test_logger.py           # Logging & correlation ID tests
│
├── docs/
│   ├── index.md
│   ├── getting-started.md
│   ├── installation.md
│   ├── api-reference.md
│   ├── async-examples.md
│   ├── examples.md
│   ├── logging.md               # Global logging documentation
│   ├── routing.md               # Route configuration documentation
│   ├── ROUTES_QUICK_REF.md      # Quick reference for routes
│   ├── HTTPS_SETUP.md           # SSL/HTTPS setup guide
│   ├── SSL_QUICK_START.md       # Quick start for SSL
│   └── CONFIG_TEST_COVERAGE.md  # Test coverage details
│
├── .env                         # Environment variables (gitignored)
├── .env.example                 # Environment variables template
├── certs/                       # SSL certificates (gitignored)
│   ├── private.key
│   └── certificate.crt
│
├── pyproject.toml               # Project configuration & dependencies
├── uv.lock                      # Locked dependency versions
├── Makefile                     # Development commands
├── setup_dev_env.py             # Development setup script
├── run.py                       # Server runner with HTTPS support
├── README.md                    # This file
└── LICENSE
```

## Generic CRUD Implementation

### Repository Pattern

```python
from app.data.v1.base_repository import BaseRepository
from app.data.v1.model.post import Post

class PostRepository(BaseRepository[Post]):
    pass

# Usage
repository = PostRepository(Post, engine)
post = repository.create(post_data)
posts = repository.read_all(skip=0, limit=10)
```

### Service Layer with DTO

```python
from app.service.v1.base_service import BaseService
from app.controller.v1.dto.post_dto import PostDto

class PostService(BaseService[Post, PostDto]):
    pass

# Usage
service = PostService(repository, Post, get_session)
post_dto = service.create(post_dto)
```

### Controller with Routing

```python
from app.controller.v1.base_controller import BaseController
from app.config.routes import get_route_config

class PostController(BaseController[Post, PostDto]):
    def __init__(self, router, service):
        super().__init__(router, service, PostDto)
        self.route_config = get_route_config("posts")
        self.register_routes()

# Endpoints automatically registered:
# POST /v1/post/         - Create
# GET /v1/post/          - Read all
# GET /v1/post/{id}      - Read one
# PUT /v1/post/{id}      - Update
# DELETE /v1/post/{id}   - Delete
```

## Centralized Route Configuration

All API endpoints are configured in one place:

```python
# src/app/config/routes.py
ROUTES = {
    "posts": RouteConfig(
        prefix="/v1/post",
        tags=["Posts"],
        description="Post management endpoints",
    ),
    # Add more routes here as app grows
}
```

Change API version/prefix in one place:

```python
API_VERSION = "v2"  # Changes all routes to /v2
```

## Global Logging with Correlation IDs

Every request is automatically tracked with a unique correlation ID:

```
[2025-12-07 10:30:15,123] [app.controller] [INFO] [correlation_id=abc-def-123] Creating post
[2025-12-07 10:30:15,124] [app.service] [INFO] [correlation_id=abc-def-123] Processing post
[2025-12-07 10:30:15,125] [app.data] [INFO] [correlation_id=abc-def-123] Saving to database
```

All logs for a single request share the same correlation ID for easy tracing.

## Environment Configuration

Configure the app via `.env` file:

```env
# Environment
ENVIRONMENT=development

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
SERVER_RELOAD=true

# HTTPS
USE_HTTPS=false
SSL_KEYFILE=./certs/private.key
SSL_CERTFILE=./certs/certificate.crt

# Database
DATABASE_URL=sqlite:///app.db

# Logging
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

## Demo Script

The demo script showcases all CRUD operations:

```bash
make demo
# or
uv run demo
```

Shows: Create, Read, Update, Delete, and List operations on Post entity.

## Documentation

Comprehensive documentation available in `docs/`:

- **Getting Started**: `docs/getting-started.md`
- **Logging System**: `docs/logging.md` and `docs/LOGGER_SETUP.md`
- **Route Configuration**: `docs/routing.md` and `docs/ROUTES_QUICK_REF.md`
- **HTTPS Setup**: `docs/HTTPS_SETUP.md` and `docs/SSL_QUICK_START.md`
- **Test Coverage**: `docs/CONFIG_TEST_COVERAGE.md`
- **API Reference**: `docs/api-reference.md`
- **Examples**: `docs/examples.md` and `docs/async-examples.md`

## Building New Entities

Follow the Post entity pattern to add new resources:

### 1. Create Model

```python
# src/app/data/v1/model/user.py
from sqlmodel import SQLModel, Field
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
```

### 2. Create DTO

```python
# src/app/controller/v1/dto/user_dto.py
from pydantic import BaseModel, ConfigDict

class UserDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = None
    name: str
    email: str
```

### 3. Create Repository

```python
# src/app/data/v1/user_repository.py
from app.data.v1.base_repository import BaseRepository
from app.data.v1.model.user import User

class UserRepository(BaseRepository[User]):
    pass
```

### 4. Create Service

```python
# src/app/service/v1/user_service.py
from app.service.v1.base_service import BaseService
from app.data.v1.model.user import User
from app.controller.v1.dto.user_dto import UserDto

class UserService(BaseService[User, UserDto]):
    pass
```

### 5. Create Controller

```python
# src/app/controller/v1/user_controller.py
from app.controller.v1.base_controller import BaseController
from app.config.routes import get_route_config
from app.data.v1.model.user import User
from app.controller.v1.dto.user_dto import UserDto
from app.service.v1.user_service import UserService

class UserController(BaseController[User, UserDto]):
    def __init__(self, router, service):
        super().__init__(router, service, UserDto)
        self.route_config = get_route_config("users")
        self.register_routes()
```

### 6. Register Route

```python
# src/app/config/routes.py
ROUTES = {
    "posts": RouteConfig(...),
    "users": RouteConfig(  # Add this
        prefix="/v1/user",
        tags=["Users"],
        description="User management endpoints",
    ),
}
```

### 7. Wire Up Controller

```python
# src/app/app.py
from app.service.v1.user_service import UserService
from app.controller.v1.user_controller import UserController

user_repository = UserRepository(User, engine)
user_service = UserService(user_repository, User, get_session)
user_controller = UserController(api_router, user_service)
```

Done! Endpoints automatically available at:
- `POST /v1/user/` - Create
- `GET /v1/user/` - List all
- `GET /v1/user/{id}` - Get one
- `PUT /v1/user/{id}` - Update
- `DELETE /v1/user/{id}` - Delete

Write tests and you're ready to deploy.

## License

MIT
