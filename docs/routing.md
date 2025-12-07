# Centralized Route Configuration

## Overview

Die Anwendung verwendet eine **zentrale Route-Konfiguration** in `src/app/config/routes.py`, die alle API-Endpunkte definiert. Dies ermöglicht:

- ✅ **Single Source of Truth**: Eine einzige Stelle für alle Endpoint-Konfigurationen
- ✅ **Scalability**: Einfaches Hinzufügen neuer Controller ohne Hardcoding
- ✅ **Consistency**: Einheitliche URL-Struktur über alle Versionen
- ✅ **Maintainability**: Zentrale Verwaltung von Präfixen und Tags

## Route Configuration Structure

### `src/app/config/routes.py`

```python
from dataclasses import dataclass

@dataclass
class RouteConfig:
    """Configuration for a single route/endpoint group."""
    prefix: str              # URL prefix (e.g., "/v1/posts")
    tags: list[str]          # OpenAPI tags for documentation
    description: str         # Description of the endpoint group

# API Version and Base Prefix
API_VERSION = "v1"
API_BASE_PREFIX = f"/{API_VERSION}"

# Central Routes Registry
ROUTES = {
    "posts": RouteConfig(
        prefix=f"{API_BASE_PREFIX}/post",
        tags=["Posts"],
        description="Post management endpoints",
    ),
    # Add new routes here as the app grows:
    # "users": RouteConfig(
    #     prefix=f"{API_BASE_PREFIX}/users",
    #     tags=["Users"],
    #     description="User management endpoints",
    # ),
}

# Helper Functions
def get_route_config(name: str) -> RouteConfig:
    """Retrieve configuration for a specific route."""
    
def get_all_routes() -> dict[str, RouteConfig]:
    """Get all registered routes."""
    
def list_routes() -> list[str]:
    """List all available route names."""
```

## How It Works

### 1. **Route Definition** (routes.py)

```python
ROUTES = {
    "posts": RouteConfig(
        prefix="/v1/post",
        tags=["Posts"],
        description="Post management endpoints",
    ),
}
```

### 2. **Router Setup** (app.py)

```python
def setup_posts_router() -> APIRouter:
    # Get configuration from central registry
    route_config = get_route_config("posts")
    
    # Create router with centralized prefix and tags
    router = APIRouter(
        prefix=route_config.prefix,
        tags=route_config.tags,
    )
    
    # Initialize controller
    PostController(router, service)
    
    return router
```

### 3. **Controller Registration** (post_controller.py)

```python
def register_routes(self) -> None:
    """Register all CRUD routes using central configuration."""
    prefix = self.route_config.prefix
    tags = self.route_config.tags
    
    @self.router.post(
        f"{prefix}/",
        response_model=PostDto,
        tags=tags,
        # ...
    )
    async def create_post(dto: PostDto) -> PostDto:
        """Create a new post."""
```

## Adding New Routes

### Step 1: Define Route Configuration

Edit `src/app/config/routes.py`:

```python
ROUTES = {
    "posts": RouteConfig(...),
    "users": RouteConfig(
        prefix=f"{API_BASE_PREFIX}/users",
        tags=["Users"],
        description="User management endpoints",
    ),
}
```

### Step 2: Create Controller

Create `src/app/controller/v1/user_controller.py`:

```python
from app.controller.v1.base_controller import BaseController
from app.config.routes import get_route_config

class UserController(BaseController[User, UserDto]):
    def __init__(self, router: APIRouter, service: UserService):
        super().__init__(router, service, UserDto)
        self.route_config = get_route_config("users")
        self.register_routes()
    
    def register_routes(self) -> None:
        prefix = self.route_config.prefix
        tags = self.route_config.tags
        
        @self.router.post(f"{prefix}/", ...)
        async def create_user(...):
            pass
```

### Step 3: Register in App

Edit `src/app/app.py`:

```python
def setup_users_router() -> APIRouter:
    route_config = get_route_config("users")
    router = APIRouter(prefix=route_config.prefix, tags=route_config.tags)
    
    service = UserService(repository)
    UserController(router, service)
    
    return router

app.include_router(setup_users_router())
```

## Current Routes

### Posts API

| Method | Endpoint | Status Code |
|--------|----------|------------|
| POST | `/v1/post/` | 201 Created |
| GET | `/v1/post/{id}` | 200 OK |
| GET | `/v1/post/` | 200 OK |
| PUT | `/v1/post/{id}` | 200 OK |
| DELETE | `/v1/post/{id}` | 204 No Content |

**Base URL**: `http://localhost:8000`

### Health Check

| Method | Endpoint | Status Code |
|--------|----------|------------|
| GET | `/health` | 200 OK |

## Benefits of Centralized Configuration

### 1. **Consistency**

Alle Controller verwenden die gleiche Konfigurationsquelle:

```python
# Alle Controller erhalten konsistent die Tags und Präfixe
route_config = get_route_config("posts")
```

### 2. **Maintainability**

URL-Änderungen an einer Stelle:

```python
# Alte Struktur
prefix="/api/v1/posts"  # Überall im Code verteilt ❌

# Neue Struktur
ROUTES = {
    "posts": RouteConfig(prefix="/api/v2/posts", ...)  # Nur hier ✅
}
```

### 3. **Documentation**

Automatische OpenAPI/Swagger Dokumentation:

```python
RouteConfig(
    description="Post management endpoints",  # Zeigt in Swagger an
)
```

### 4. **Discovery**

Alle verfügbaren Routes können abgerufen werden:

```python
routes = list_routes()  # ["posts", "users", "comments"]
for route in routes:
    config = get_route_config(route)
    print(f"{route}: {config.prefix}")
```

## API Version Management

### Current Version

```python
API_VERSION = "v1"
API_BASE_PREFIX = f"/{API_VERSION}"  # "/v1"
```

### Upgrading to v2

```python
# routes.py
API_VERSION = "v2"
API_BASE_PREFIX = f"/{API_VERSION}"  # "/v2"

ROUTES = {
    "posts": RouteConfig(
        prefix=f"{API_BASE_PREFIX}/posts",  # Automatically becomes "/v2/posts"
        ...
    ),
}
```

## Example: Adding a Comments API

### 1. Define Route

```python
# src/app/config/routes.py
ROUTES = {
    "posts": RouteConfig(...),
    "comments": RouteConfig(
        prefix=f"{API_BASE_PREFIX}/comments",
        tags=["Comments"],
        description="Comment management endpoints",
    ),
}
```

### 2. Create Model & DTO

```python
# src/app/data/v1/model/comment.py
class Comment(SQLModel, table=True):
    id: Optional[int] = None
    post_id: int
    content: str
    author: str

# src/app/controller/v1/dto/comment_dto.py
class CommentDto(BaseModel):
    id: Optional[int] = None
    post_id: int
    content: str
    author: str
```

### 3. Create Controller

```python
# src/app/controller/v1/comment_controller.py
class CommentController(BaseController[Comment, CommentDto]):
    def __init__(self, router: APIRouter, service: CommentService):
        super().__init__(router, service, CommentDto)
        self.route_config = get_route_config("comments")
        self.register_routes()
    
    def register_routes(self) -> None:
        prefix = self.route_config.prefix
        # Register routes...
```

### 4. Register in App

```python
# src/app/app.py
def setup_comments_router() -> APIRouter:
    route_config = get_route_config("comments")
    router = APIRouter(prefix=route_config.prefix, tags=route_config.tags)
    
    repository = CommentRepository(session)
    service = CommentService(repository)
    CommentController(router, service)
    
    return router

app.include_router(setup_comments_router())
```

## Helper Functions

### Get Specific Route

```python
from app.config.routes import get_route_config

route = get_route_config("posts")
print(route.prefix)        # "/v1/post"
print(route.tags)          # ["Posts"]
print(route.description)   # "Post management endpoints"
```

### Get All Routes

```python
from app.config.routes import get_all_routes

all_routes = get_all_routes()
for name, config in all_routes.items():
    print(f"{name}: {config.prefix}")
```

### List Route Names

```python
from app.config.routes import list_routes

names = list_routes()  # ["posts", "users", "comments"]
```

## Best Practices

✅ **DO:**
- Centralize all route definitions in `routes.py`
- Use `get_route_config()` in controllers
- Keep API_VERSION in one place
- Add descriptions for Swagger documentation
- Group related endpoints with the same base prefix

❌ **DON'T:**
- Hardcode prefixes in controllers
- Scatter route definitions across files
- Create inconsistent naming patterns
- Forget to add route descriptions

## Migration Path

If you have existing hardcoded routes:

### Before
```python
# controller/post_controller.py
router = APIRouter(prefix="/api/v1/posts", tags=["Posts"])
```

### After
```python
# routes.py
ROUTES = {
    "posts": RouteConfig(
        prefix="/api/v1/posts",
        tags=["Posts"],
        description="Post management endpoints",
    ),
}

# controller/post_controller.py
route_config = get_route_config("posts")
router = APIRouter(prefix=route_config.prefix, tags=route_config.tags)
```

## Testing Routes

```python
from app.config.routes import get_route_config, list_routes

def test_routes_configured():
    """Verify all routes are properly configured."""
    routes = list_routes()
    assert "posts" in routes
    
    config = get_route_config("posts")
    assert config.prefix == "/v1/post"
    assert "Posts" in config.tags
```

---

Diese zentrale Route-Konfiguration ist das Fundament für eine skalierbare, wartbare FastAPI-Anwendung! 🚀
