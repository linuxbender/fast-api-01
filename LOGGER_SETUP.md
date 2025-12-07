# 🔍 Logger-Setup mit Correlation ID

## ✅ Was wurde implementiert

### 1. Globale Logger-Konfiguration (`src/app/config/logger.py`)
- **CorrelationIdFilter**: Python logging Filter, injiziert Correlation ID
- **CorrelationIdFormatter**: Custom Formatter mit Correlation ID im Format
- **setup_logging()**: Globale Logger-Initialisierung
- **get_logger(name)**: Factory für Logger mit Correlation ID Support
- **ContextVar-basiert**: Thread-safe und Async-safe

### 2. Correlation ID Middleware (`src/app/config/correlation_id_middleware.py`)
- Liest/generiert `X-Correlation-ID` Header
- Setzt ID im Context für gesamten Request
- Loggt Request-Start und -Abschluss
- Fügt ID zu Response-Header hinzu

### 3. App-Integration (`src/app/app.py`)
```python
from app.config.correlation_id_middleware import CorrelationIdMiddleware

app.add_middleware(CorrelationIdMiddleware)
```

## 📋 Log-Format

```
[TIMESTAMP] [LOGGER_NAME] [LEVEL] [correlation_id=ID] MESSAGE
```

**Beispiel:**
```
[2025-12-07 01:46:05,701] [app.service.post] [INFO] [correlation_id=abc12345] Creating new post
[2025-12-07 01:46:05,702] [app.data.repository] [INFO] [correlation_id=abc12345] Saving to database
```

## 🚀 Verwendung

### In beliebigem Modul
```python
from app.config.logger import get_logger

logger = get_logger(__name__)

logger.info("Doing something")
logger.error("An error occurred", exc_info=True)

# Correlation ID wird AUTOMATISCH hinzugefügt!
```

### Correlation ID manuell setzen
```python
from app.config.logger import set_correlation_id

set_correlation_id("CUSTOM-ID-12345")
```

## 📊 Vorteile

✅ **Automatisches Tracking**: Jeder Log hat eindeutige Correlation ID  
✅ **Verteilte Systeme**: ID über Services propagierbar  
✅ **Debugging**: Alle Logs für einen Request zusammen nachverfolgbar  
✅ **Monitoring**: Integration mit ELK, Datadog, etc.  
✅ **Performance**: Context-basiert, kein Overhead  

## 📁 Dateien

- `src/app/config/logger.py` - Logger-Konfiguration
- `src/app/config/correlation_id_middleware.py` - Middleware
- `src/app/config/logger_examples.py` - Beispiele
- `docs/logging.md` - Ausführliche Dokumentation

## ✅ Tests

Alle 17 Tests bestehen ✅
