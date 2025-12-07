# Quick Reference: Centralized Routes

## Files Involved

```
src/app/
├── config/
│   └── routes.py              # ← Central route configuration
├── app.py                      # Uses get_route_config("posts")
└── controller/v1/
    └── post_controller.py      # Uses get_route_config("posts")
```

## Current Setup

```
routes.py
  ↓
  ROUTES = {
    "posts": RouteConfig(prefix="/v1/post", tags=["Posts"])
  }
  ↓
app.py (setup_posts_router)
  ↓
post_controller.py (register_routes)
  ↓
FastAPI App
```

## Example: Adding Users Route

### 1. Edit `routes.py`

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

### 2. Create `user_controller.py`

```python
from app.config.routes import get_route_config

class UserController(BaseController[User, UserDto]):
    def __init__(self, router, service):
        super().__init__(router, service, UserDto)
        self.route_config = get_route_config("users")
        self.register_routes()
    
    def register_routes(self):
        prefix = self.route_config.prefix
        # ... define routes
```

### 3. Edit `app.py`

```python
def setup_users_router():
    route_config = get_route_config("users")
    router = APIRouter(prefix=route_config.prefix, tags=route_config.tags)
    service = UserService(repository)
    UserController(router, service)
    return router

app.include_router(setup_users_router())
```

## API Endpoints

### Posts
- `POST /v1/post/` - Create
- `GET /v1/post/{id}` - Read
- `GET /v1/post/` - Read All (with pagination)
- `PUT /v1/post/{id}` - Update
- `DELETE /v1/post/{id}` - Delete

### Health
- `GET /health` - Health check
- `GET /` - Welcome

## Key Functions

```python
from app.config.routes import get_route_config, list_routes, get_all_routes

# Get config for specific route
config = get_route_config("posts")
# → RouteConfig(prefix="/v1/post", tags=["Posts"], description="...")

# List all route names
names = list_routes()
# → ["posts"]

# Get all routes
all_routes = get_all_routes()
# → {"posts": RouteConfig(...)}
```

## Change Prefix

To change from `/v1/post` to `/api/v1/posts`:

```python
# routes.py
ROUTES = {
    "posts": RouteConfig(
        prefix="/api/v1/posts",  # ← Change here only!
        tags=["Posts"],
        description="Post management endpoints",
    ),
}
```

That's it! No other changes needed. ✅

## Upgrade to v2

To upgrade entire API to v2:

```python
# routes.py
API_VERSION = "v2"
API_BASE_PREFIX = f"/{API_VERSION}"  # Now "/v2"

# All routes automatically use "/v2" prefix
ROUTES = {
    "posts": RouteConfig(
        prefix=f"{API_BASE_PREFIX}/post",  # Becomes "/v2/post"
        ...
    ),
}
```

---

**Principle:** One change, one location, zero scattered configuration! 🎯
