# API Reference

Dokumentation aller verfügbaren API-Endpoints.

## Base URL

```
http://127.0.0.1:8000
```

## Endpoints

### GET /

Root endpoint der API.

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
- `200 OK` - Erfolgreiche Anfrage

---

### GET /items/{item_id}

Ruft ein Item anhand seiner ID ab.

**Parameters**

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `item_id` | integer | path | Yes | Die ID des Items |
| `q` | string | query | No | Optionaler Suchparameter |

**Response**

```json
{
  "item_id": 42,
  "q": "test"
}
```

**Examples**

```bash
# Mit Query Parameter
curl http://127.0.0.1:8000/items/42?q=test

# Ohne Query Parameter
curl http://127.0.0.1:8000/items/42
```

**Response Codes**
- `200 OK` - Item gefunden
- `422 Unprocessable Entity` - Ungültige Parameter

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

Wird zurückgegeben, wenn die Request-Parameter ungültig sind.

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

FastAPI bietet automatische, interaktive API-Dokumentation:

- **Swagger UI**: http://127.0.0.1:8000/docs
  - Interaktive API-Tests direkt im Browser
  - Automatisch generierte Request/Response Schemas

- **ReDoc**: http://127.0.0.1:8000/redoc
  - Alternative Dokumentationsansicht
  - Übersichtlicher für große APIs

## Python Client Beispiel

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

Siehe `tests/test_app.py` für Test-Beispiele mit dem FastAPI TestClient.

```python
from fastapi.testclient import TestClient
from fastapi_01.app import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World with FastAPI"}
```
