# Installation

## Voraussetzungen

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) Package Manager

## UV installieren

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Mit Homebrew (macOS)
brew install uv
```

## Projekt Setup

### 1. Repository klonen

```bash
git clone <repository-url>
cd FastAPI_01
```

### 2. Dependencies installieren

#### Nur Production Dependencies

```bash
make install
# oder
uv pip install -e .
```

#### Alle Dependencies (inkl. Dev-Tools)

```bash
make install-dev
# oder
uv pip install -e ".[dev]"
```

### 3. Virtual Environment

UV erstellt automatisch ein Virtual Environment im `.venv/` Ordner.

### 4. Projekt testen

```bash
# Tests ausführen
make test

# Server starten
make run
```

## Manuelle Installation ohne Makefile

```bash
# Virtual Environment erstellen
uv venv

# Aktivieren
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Dependencies installieren
uv pip install -e ".[dev]"

# Tests ausführen
uv run pytest

# Server starten
uv run uvicorn fastapi_01.app:app --reload
```

## Entwicklungsumgebung

### Empfohlene IDE

- **VS Code** mit Python Extension
- **PyCharm** Professional oder Community

### VS Code Extensions

- Python
- Pylance
- Ruff (Linting & Formatting)

## Nächste Schritte

- [Getting Started Guide](getting-started.md)
- [API Reference](api-reference.md)
