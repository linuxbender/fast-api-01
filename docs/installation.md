# Installation

## Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) Package Manager

## Install UV

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# With Homebrew (macOS)
brew install uv
```

## Project Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd FastAPI_01
```

### 2. Install Dependencies

#### Production Dependencies Only

```bash
make install
# or
uv pip install -e .
```

#### All Dependencies (including Dev Tools)

```bash
make install-dev
# or
uv pip install -e ".[dev]"
```

### 3. Virtual Environment

UV automatically creates a virtual environment in the `.venv/` folder.

### 4. Test the Project

```bash
# Run tests
make test

# Start server
make run
```

## Manual Installation without Makefile

```bash
# Create virtual environment
uv venv

# Activate
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install dependencies
uv pip install -e ".[dev]"

# Run tests
uv run pytest

# Start server
uv run uvicorn fastapi_01.app:app --reload
```

## Development Environment

### Recommended IDE

- **VS Code** with Python Extension
- **PyCharm** Professional or Community

### VS Code Extensions

- Python
- Pylance
- Ruff (Linting & Formatting)

## Next Steps

- [Getting Started Guide](getting-started.md)
- [API Reference](api-reference.md)
