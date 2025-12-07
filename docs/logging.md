# Logging mit Correlation ID

## Übersicht

Das Logger-System ist global konfiguriert mit **Correlation ID Tracking**. Jede Log-Nachricht enthält automatisch eine eindeutige `correlation_id`, die über den gesamten Request-Lifecycle hinweg konsistent bleibt.

## Features

- ✅ **Globale Correlation ID**: Automatisch in jedem Log enthalten
- ✅ **Request-Tracking**: Jeder Request bekommt eine eindeutige ID
- ✅ **Context-basiert**: Verwendet Python `contextvars` für Thread-sicherheit
- ✅ **Middleware-Integration**: Automatische ID-Verwaltung in FastAPI
- ✅ **Header-Propagation**: `X-Correlation-ID` Header in Requests/Responses

## Log-Format

```
[TIMESTAMP] [LOGGER_NAME] [LEVEL] [correlation_id=ID] MESSAGE
```

**Beispiel:**
```
[2025-12-07 01:46:05,701] [app.service.post] [INFO] [correlation_id=a1b2c3d4] Creating new post
[2025-12-07 01:46:05,702] [app.data.repository] [INFO] [correlation_id=a1b2c3d4] Saving to database
[2025-12-07 01:46:05,703] [app.controller.post] [INFO] [correlation_id=a1b2c3d4] Post created successfully
```

## Verwendung

### 1. Logger in Modul importieren und verwenden

```python
from app.config.logger import get_logger

logger = get_logger(__name__)

# Logger wird automatisch mit Correlation ID aus Context verwaltet
logger.info("Doing something important")
logger.error("An error occurred", exc_info=True)
```

### 2. Correlation ID manuell setzen (falls notwendig)

```python
from app.config.logger import set_correlation_id, get_correlation_id

# Correlation ID setzen
set_correlation_id("CUSTOM-ID-12345")

# Correlation ID abrufen
current_id = get_correlation_id()
```

### 3. In HTTP Requests

Die Middleware fügt automatisch die Correlation ID hinzu:

**Request Header:**
```
X-Correlation-ID: a1b2c3d4
```

**Response Header:**
```
X-Correlation-ID: a1b2c3d4
```

Oder manuell setzen:
```bash
curl -H "X-Correlation-ID: my-custom-id" http://localhost:8000/api/v1/posts/
```

## Komponenten

### 1. `logger.py` - Logger Konfiguration
- `setup_logging()`: Initialisiert globales Logger-Setup
- `get_logger(name)`: Erstellt Logger mit Correlation ID Support
- `get_correlation_id()`: Ruft aktuelle Correlation ID ab
- `set_correlation_id(id)`: Setzt Correlation ID für aktuellen Context
- `generate_correlation_id()`: Generiert neue UUID

### 2. `correlation_id_middleware.py` - FastAPI Middleware
- Generiert/liest Correlation ID für jeden Request
- Setzt ID im Context für die gesamte Request-Duration
- Fügt ID zu Response Headers hinzu
- Loggt Request-Start und -Abschluss

### 3. App Integration (`app.py`)
```python
from app.config.correlation_id_middleware import CorrelationIdMiddleware

# Middleware als erstes hinzufügen (vor anderen Middlewares)
app.add_middleware(CorrelationIdMiddleware)
```

## Log-Levels

Die folgenden Log-Levels werden verwendet:

- **DEBUG**: Detaillierte Debugging-Informationen
- **INFO**: Allgemeine Informationen über Programmablauf
- **WARNING**: Warnungen für potenzielle Probleme
- **ERROR**: Fehler mit vollem Stack Trace (`exc_info=True`)

## Beispiele

### Einfaches Logging

```python
logger = get_logger(__name__)

logger.info("User logged in")
logger.warning("Unused parameter detected")
logger.error("Failed to connect to database", exc_info=True)
```

### Mit Kontext

```python
logger.info(f"Processing order {order_id} for user {user_id}")
logger.debug(f"Payload: {data}")
```

### In Services

```python
class UserService(BaseService[User, UserDto]):
    def __init__(self, repository):
        super().__init__(repository, User, UserDto)
        self.logger = get_logger(__name__)
    
    def create(self, dto: UserDto) -> UserDto:
        self.logger.info(f"Creating user: {dto.name}")
        result = super().create(dto)
        self.logger.info(f"User created with ID: {result.id}")
        return result
```

## Testing

Logs in Tests:

```python
def test_create_user(self, user_service: UserService):
    """Test user creation with logging."""
    dto = UserDto(name="John")
    
    # Logger wird automatisch mit NO_CORRELATION_ID ausgeführt in Tests
    result = user_service.create(dto)
    
    assert result.id is not None
```

## Production-Ready Features

✅ Thread-safe (`contextvars`)  
✅ Asynchronous-safe (für FastAPI)  
✅ Strukturiertes Logging mit Correlation IDs  
✅ Einfache Integration mit Monitoring/Tracing (z.B. ELK Stack, Datadog)  
✅ Automatische Header-Propagation für Microservices  

## Konfiguration anpassen

### Log-Level ändern

```python
from app.config.logger import setup_logging
import logging

# DEBUG-Level für Development
setup_logging(level=logging.DEBUG)
```

### Format anpassen

```python
from app.config.logger import CorrelationIdFormatter
import logging

fmt = "[%(levelname)s] [%(correlation_id)s] %(message)s"
formatter = CorrelationIdFormatter(fmt=fmt)
```

## Integration mit externen Logging-Services

Für Integration mit ELK Stack, Datadog, oder ähnlichen Services können die Log-Ausgaben leicht umgeleitet werden:

```python
# JSON-Formatter für strukturierte Logs
import json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "correlation_id": getattr(record, 'correlation_id', 'N/A'),
            "message": record.getMessage()
        }
        return json.dumps(log_data)
```

## Best Practices

1. **Immer `get_logger(__name__)` verwenden** - Aussagekräftige Logger-Namen
2. **Correlation ID wird automatisch verwaltet** - Nicht manuell setzen außer Nötig
3. **Verwende passende Log-Levels** - DEBUG/INFO/WARNING/ERROR richtig wählen
4. **Bei Exceptions `exc_info=True`** - Für Stack Traces
5. **In Produktiv-Umgebung DEBUG deaktivieren** - Performance

---

**Beispiel:** `uv run python src/app/config/logger_examples.py`
