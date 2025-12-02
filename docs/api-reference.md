# API Reference

Documentation of all available API endpoints.

## Base URL

```
http://127.0.0.1:8000
```

## Endpoints

### GET /

Root endpoint of the API.

**Response**

```json
{
  "message": "Hello World with FastAPI"
}
```

**Example**

```bash
curl http://127.0.0.1:8000/
```

**Response Code**
- `200 OK` - Successful request

---

### GET /items/{item_id}

Retrieves an item by its ID.

**Parameters**

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `item_id` | integer | path | Yes | The ID of the item |
| `q` | string | query | No | Optional search parameter |

**Response**

```json
{
  "item_id": 42,
  "q": "test"
}
```

**Examples**

```bash
# With query parameter
curl http://127.0.0.1:8000/items/42?q=test

# Without query parameter
curl http://127.0.0.1:8000/items/42
```

**Response Codes**
- `200 OK` - Item found
- `422 Unprocessable Entity` - Invalid parameters

---

## Response Models

### Item Response

```python
{
  "item_id": int,
  "q": str | None
}
```

## Error Responses

### Validation Error (422)

Returned when request parameters are invalid.

```json
{
  "detail": [
    {
      "loc": ["path", "item_id"],
      "msg": "value is not a valid integer",
      "type": "type_error.integer"
    }
  ]
}
```

## Interactive Documentation

FastAPI provides automatic, interactive API documentation:

- **Swagger UI**: http://127.0.0.1:8000/docs
  - Interactive API tests directly in the browser
  - Automatically generated Request/Response schemas

- **ReDoc**: http://127.0.0.1:8000/redoc
  - Alternative documentation view
  - Clearer overview for large APIs

## Python Client Example

```python
import httpx

# GET Root
response = httpx.get("http://127.0.0.1:8000/")
print(response.json())
# {"message": "Hello World with FastAPI"}

# GET Item
response = httpx.get("http://127.0.0.1:8000/items/42", params={"q": "test"})
print(response.json())
# {"item_id": 42, "q": "test"}
```

## Testing

See `tests/test_app.py` for test examples with the FastAPI TestClient.

```python
from fastapi.testclient import TestClient
from fastapi_01.app import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World with FastAPI"}
```
