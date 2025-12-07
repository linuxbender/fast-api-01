# SSL/HTTPS Configuration für Local Development

## Overview

Die FastAPI-Anwendung unterstützt HTTPS mit selbstsigniertem Zertifikat für lokale Entwicklung.

## Setup

### Schritt 1: SSL-Zertifikate generieren

```bash
# Automatisches Setup (empfohlen)
make setup-ssl

# Oder manuell
uv run python setup_dev_env.py
```

Dies generiert:
- `certs/private.key` - Private RSA-Schlüssel
- `certs/certificate.crt` - Selbstsigniertes Zertifikat (gültig für 365 Tage)
- `.env` - Konfigurationsdatei

### Schritt 2: HTTPS aktivieren

**Option A: Direkt mit make**

```bash
# HTTP (default)
make run

# HTTPS
make run-https
```

**Option B: Mit .env konfigurieren**

Bearbeite `.env`:

```env
USE_HTTPS=true
SSL_KEYFILE=./certs/private.key
SSL_CERTFILE=./certs/certificate.crt
```

Starte dann den Server normal:

```bash
make run
# oder
uv run python run.py
```

**Option C: Mit Kommandozeile**

```bash
uv run python run.py --https
```

## Umgebungsvariablen

### Für Development

Erstelle eine `.env` Datei (wird von `setup_dev_env.py` erstellt):

```env
# Environment
ENVIRONMENT=development

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
SERVER_RELOAD=true

# HTTPS/SSL Configuration
USE_HTTPS=false
SSL_KEYFILE=./certs/private.key
SSL_CERTFILE=./certs/certificate.crt

# Database
DATABASE_URL=sqlite:///app.db

# Logging
LOG_LEVEL=INFO

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000","http://127.0.0.1:8000"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["GET","POST","PUT","DELETE","OPTIONS"]
CORS_ALLOW_HEADERS=["*"]
```

## Certificate Information

Nach der Generierung:

```
Subject: CN=localhost,O=FastAPI Dev,L=Local,ST=Bavaria,C=DE
Issuer: CN=localhost,O=FastAPI Dev,L=Local,ST=Bavaria,C=DE
Serial Number: ...
Not Before: 2025-12-07 01:08:53
Not After: 2026-12-07 01:08:53
Valid Days: 365
```

Gültig für: **localhost**, **.localhost**, **127.0.0.1**

## Browser Warning

Da das Zertifikat selbstsigniert ist, zeigen Browser eine Warnung an:

### Chrome/Edge
```
🔒 Deine Verbindung ist nicht privat
```
→ Klicke "Advanced" → "Proceed to localhost (unsafe)"

### Firefox
```
⚠️  Warnung: Mögliches Sicherheitsrisiko erkannt
```
→ Klicke "Advanced" → "Accept the Risk and Continue"

### Safari
```
Safari kann die Website nicht öffnen
```
→ Klicke ">>" → "Show Certificate" → "Always Trust"

## run.py - Server Runner

```bash
# HTTP (default)
uv run python run.py

# HTTPS
uv run python run.py --https

# Custom Port
uv run python run.py --port 9000

# Custom Host
uv run python run.py --host 127.0.0.1

# Ohne Auto-reload (Production-ähnlich)
uv run python run.py --no-reload

# Mit mehreren Worker-Prozessen
uv run python run.py --workers 4

# Help
uv run python run.py --help
```

## ssl_generator.py - Zertifikat Generator

```bash
# Zertifikate generieren/regenerieren
uv run python -m app.config.ssl_generator

# Mit Custom Directory
uv run python -m app.config.ssl_generator --cert-dir ./my_certs

# Mit Custom Gültigkeitsdauer (Tage)
uv run python -m app.config.ssl_generator --days 730

# Force regenerate
uv run python -m app.config.ssl_generator --force
```

## settings.py - Environment Configuration

Die `app/config/settings.py` Datei verwaltet alle Konfigurationen:

```python
from app.config.settings import get_settings, should_use_https, is_development

# Aktuelle Settings abrufen
settings = get_settings()

# Umgebung prüfen
if is_development():
    print("In development mode")

# HTTPS prüfen
if should_use_https():
    print("HTTPS ist aktiviert und Zertifikate existieren")

# Spezifische Setting abrufen
host = settings.server_host
port = settings.server_port
log_level = settings.log_level
```

## API URLs

### HTTP
```
http://localhost:8000
http://localhost:8000/docs (Swagger UI)
http://localhost:8000/redoc (ReDoc)
```

### HTTPS
```
https://localhost:8000
https://localhost:8000/docs (Swagger UI)
https://localhost:8000/redoc (ReDoc)
```

## Troubleshooting

### Problem: "Certificate not found"

```
❌ Error: HTTPS requested but certificates not found
```

**Lösung:**
```bash
make setup-ssl
```

### Problem: "Port already in use"

```bash
# Anderen Port verwenden
uv run python run.py --port 9000

# Oder Make-target
SERVER_PORT=9000 make run
```

### Problem: Browser zeigt immer noch Warnung

- Browser-Cache löschen
- Inkognito/Private-Fenster nutzen
- Zertifikat regenerieren: `make setup-ssl --force`

### Problem: CORS-Fehler

Passe `CORS_ORIGINS` in `.env` an:

```env
CORS_ORIGINS=["http://localhost:3000","https://localhost:8000"]
```

## Best Practices

✅ **DO:**
- Verwende HTTPS nur für lokale Entwicklung
- Regeneriere Zertifikate regelmäßig
- `.env` Datei nie in Git committen
- `certs/` Directory in `.gitignore` halten

❌ **DON'T:**
- Selbstsignierte Zertifikate in Production verwenden
- `.env` Datei in Version Control committen
- SSL-Schlüssel in Code hardcoden
- Zertifikat-Dateien in Public Repositories teilen

## Produktions-Setup

Für Production mit echten Zertifikaten:

1. **Let's Encrypt verwenden:**
   ```bash
   uv add certbot
   ```

2. **Oder kommerzielles Zertifikat kaufen**

3. **Uvicorn mit Production-Settings:**
   ```bash
   uv run uvicorn app.app:app \
       --host 0.0.0.0 \
       --port 443 \
       --ssl-keyfile=/etc/ssl/private/key.pem \
       --ssl-certfile=/etc/ssl/certs/cert.pem \
       --workers 4
   ```

4. **Oder Reverse Proxy verwenden (empfohlen):**
   - Nginx
   - Apache
   - Caddy

## Dateistruktur

```
FastAPI_01/
├── .env                           # ← Environment variables (gitignored)
├── setup_dev_env.py               # ← Setup-Skript
├── run.py                         # ← Server Runner mit HTTPS
├── certs/                         # ← Zertifikate (gitignored)
│   ├── private.key               # ← Private Schlüssel
│   └── certificate.crt           # ← Zertifikat
└── src/app/config/
    ├── settings.py               # ← Environment-Konfiguration
    ├── ssl_generator.py          # ← Zertifikat-Generator
    └── correlation_id_middleware # ← Request Tracking
```

## Verwendungsbeispiele

### Entwicklung mit HTTP

```bash
make run
# oder
uv run python run.py
```

### Entwicklung mit HTTPS

```bash
make run-https
# oder
uv run python run.py --https
```

### Mit curl testen

```bash
# HTTP
curl http://localhost:8000/health

# HTTPS (mit selbstsigniertem Zertifikat)
curl --insecure https://localhost:8000/health
curl -k https://localhost:8000/health

# Mit Zertifikat-Datei
curl --cacert certs/certificate.crt https://localhost:8000/health
```

### Mit Python requests

```python
import requests

# HTTP
response = requests.get("http://localhost:8000/health")

# HTTPS (warnt vor selbstsigniertem Zertifikat)
response = requests.get("https://localhost:8000/health", verify=False)

# Oder mit Zertifikat
response = requests.get(
    "https://localhost:8000/health",
    verify="certs/certificate.crt"
)
```

---

**Hinweis**: Selbstsignierte Zertifikate sollten **NUR** für lokale Entwicklung verwendet werden! 🔒
