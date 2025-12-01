# Examples

Praktische Code-Beispiele und Patterns für FastAPI 01.

## Basis Beispiele

### Einfacher GET Endpoint

```python
@app.get("/hello")
def hello() -> dict[str, str]:
    return {"message": "Hello World"}
```

### Path Parameter

```python
@app.get("/users/{user_id}")
def get_user(user_id: int) -> dict[str, int]:
    return {"user_id": user_id}
```

### Query Parameter

```python
@app.get("/search")
def search(q: str, limit: int = 10) -> dict[str, str | int]:
    return {"query": q, "limit": limit}
```

### Optionale Parameter

```python
@app.get("/items/{item_id}")
def get_item(item_id: int, details: bool = False) -> dict:
    if details:
        return {"item_id": item_id, "name": "Item", "price": 99.99}
    return {"item_id": item_id}
```

## Pydantic Models

### Request Body mit Model

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float
    description: str | None = None

@app.post("/items")
def create_item(item: Item) -> Item:
    return item
```

### Response Model

```python
class UserResponse(BaseModel):
    id: int
    username: str
    email: str

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int) -> UserResponse:
    return UserResponse(
        id=user_id,
        username="john",
        email="john@example.com"
    )
```

## Fortgeschrittene Patterns

### Dependency Injection

```python
from fastapi import Depends

def get_db():
    db = DatabaseConnection()
    try:
        yield db
    finally:
        db.close()

@app.get("/users")
def list_users(db = Depends(get_db)):
    return db.query("SELECT * FROM users")
```

### Background Tasks

```python
from fastapi import BackgroundTasks

def send_email(email: str, message: str):
    # Send email logic
    print(f"Sending email to {email}: {message}")

@app.post("/send-notification")
def send_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_email, email, "Hello!")
    return {"message": "Notification scheduled"}
```

### Error Handling

```python
from fastapi import HTTPException

@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id > 1000:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )
    return {"item_id": item_id}
```

## Testing Patterns

### Basic Test

```python
def test_endpoint(client: TestClient):
    response = client.get("/endpoint")
    assert response.status_code == 200
```

### POST Request Test

```python
def test_create_item(client: TestClient):
    response = client.post(
        "/items",
        json={"name": "Test", "price": 9.99}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test"
```

### Test mit Headers

```python
def test_with_auth(client: TestClient):
    headers = {"Authorization": "Bearer token123"}
    response = client.get("/protected", headers=headers)
    assert response.status_code == 200
```

## Configuration

### Environment Variables

Erstelle eine `.env` Datei:

```env
DATABASE_URL=postgresql://user:pass@localhost/db
SECRET_KEY=your-secret-key-here
DEBUG=true
```

Verwende in der App:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
```

## CORS

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Static Files

```python
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```

## Weitere Ressourcen

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Starlette Documentation](https://www.starlette.io/)
