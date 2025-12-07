# SSL/HTTPS Setup für Local Development 🔒

## Quick Start

```bash
# 1. Zertifikate generieren
make setup-ssl

# 2. Server mit HTTPS starten
make run-https

# 3. Im Browser öffnen
# https://localhost:8000/docs
# (Zertifikat-Warnung akzeptieren)
```

## Was wurde eingerichtet

✅ **Self-Signed Zertifikate**
- `certs/private.key` - Private Schlüssel
- `certs/certificate.crt` - Zertifikat (gültig für 365 Tage)

✅ **Environment-Konfiguration (.env)**
- `USE_HTTPS` - HTTPS aktivieren/deaktivieren
- `SSL_KEYFILE` - Pfad zum Private Key
- `SSL_CERTFILE` - Pfad zum Zertifikat
- Alle anderen Server-Einstellungen

✅ **Setup-Skripte**
- `setup_dev_env.py` - Automatisches Setup aller Komponenten
- `run.py` - Server Runner mit HTTPS Support
- `src/app/config/ssl_generator.py` - Zertifikat-Generator
- `src/app/config/settings.py` - Environment-Verwaltung

## Verwendung

### HTTP (Default)

```bash
# Mit Make
make run

# Oder direkt
uv run python run.py
```

→ http://localhost:8000

### HTTPS

```bash
# Mit Make
make run-https

# Oder direkt
uv run python run.py --https
```

→ https://localhost:8000

### Custom Settings

```bash
# Mit anderem Port
uv run python run.py --port 9000

# Mit anderem Host
uv run python run.py --host 127.0.0.1

# Ohne Auto-reload
uv run python run.py --no-reload

# Mit mehreren Workers
uv run python run.py --workers 4
```

## .env Konfiguration

Die `.env` Datei wird automatisch bei `setup_dev_env.py` erstellt:

```env
# Umgebung
ENVIRONMENT=development

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
SERVER_RELOAD=true

# HTTPS - Ändere zu 'true' um HTTPS zu aktivieren
USE_HTTPS=false
SSL_KEYFILE=./certs/private.key
SSL_CERTFILE=./certs/certificate.crt

# Database
DATABASE_URL=sqlite:///app.db

# Logging
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["GET","POST","PUT","DELETE","OPTIONS"]
CORS_ALLOW_HEADERS=["*"]
```

## Zertifikate neu generieren

```bash
# Mit Setup-Skript
make setup-ssl

# Oder direkt
uv run python -m app.config.ssl_generator --force
```

## Browser-Warnungen

Weil das Zertifikat selbstsigniert ist, zeigen Browser Warnungen an:

### Chrome/Edge
Klicke "Advanced" → "Proceed to localhost (unsafe)"

### Firefox
Klicke "Advanced" → "Accept the Risk and Continue"

### Safari
Klicke ">>" → "Show Certificate" → "Always Trust"

## Testing mit curl

```bash
# HTTP
curl http://localhost:8000/health

# HTTPS (mit selbstsigniertem Cert)
curl --insecure https://localhost:8000/health
curl -k https://localhost:8000/health

# Mit Zertifikat
curl --cacert certs/certificate.crt https://localhost:8000/health
```

## Python Testing

```python
import requests

# HTTP
response = requests.get("http://localhost:8000/health")

# HTTPS (ignoriere Zertifikat-Warnung)
response = requests.get("https://localhost:8000/health", verify=False)
```

## Dokumentation

Siehe `docs/HTTPS_SETUP.md` für ausführliche Dokumentation mit:
- Detailliertes Setup
- Umgebungsvariablen
- Troubleshooting
- Production Best Practices

---

**Hinweis**: Diese Zertifikate sind nur für **lokale Entwicklung** gedacht! 🔓
