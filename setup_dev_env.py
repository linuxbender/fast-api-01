#!/usr/bin/env python3
"""
Development Environment Setup Script

This script:
1. Creates SSL certificates for local development
2. Generates or updates .env configuration
3. Initializes the development environment

Usage:
    python setup_dev_env.py
"""

import subprocess
import sys
from pathlib import Path


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"🚀 {text}")
    print("=" * 60)


def print_success(text: str):
    """Print success message."""
    print(f"✅ {text}")


def print_info(text: str):
    """Print info message."""
    print(f"ℹ️  {text}")


def print_error(text: str):
    """Print error message."""
    print(f"❌ {text}")


def generate_ssl_certificates():
    """Generate self-signed SSL certificates."""
    print_header("Generating SSL Certificates")

    try:
        result = subprocess.run(
            ["uv", "run", "python", "-m", "app.config.ssl_generator", "--force"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            if "cryptography" in result.stderr:
                print_error("cryptography module not found")
                print_info("Install it with: uv add cryptography")
                return False
            print_error(f"Failed to generate certificates: {result.stderr}")
            return False

        print(result.stdout)
        return True

    except Exception as e:
        print_error(f"Error generating certificates: {e}")
        return False


def create_env_file():
    """Create or update .env file."""
    print_header("Setting Up .env Configuration")

    env_file = Path(".env")
    env_template = """\
# FastAPI Application Configuration - Development Environment
# This file is gitignored and should not be committed to version control

# Environment
ENVIRONMENT=development

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
SERVER_RELOAD=true

# HTTPS/SSL Configuration (Required for all environments)
# Self-signed certificates are auto-generated if not present
SSL_KEYFILE=./certs/private.key
SSL_CERTFILE=./certs/certificate.crt

# Database
DATABASE_URL=sqlite:///app.db

# Logging
LOG_LEVEL=DEBUG

# CORS Configuration
CORS_ORIGINS=["https://localhost:3000","https://localhost:8000","https://127.0.0.1:8000"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["GET","POST","PUT","DELETE","OPTIONS"]
CORS_ALLOW_HEADERS=["*"]
"""

    if env_file.exists():
        print_info(".env file already exists")
        response = input("Overwrite? (y/n) [n]: ").strip().lower()
        if response != "y":
            return True

    try:
        env_file.write_text(env_template)
        print_success(f".env file created: {env_file.absolute()}")
        return True
    except Exception as e:
        print_error(f"Failed to create .env file: {e}")
        return False


def verify_environment():
    """Verify the development environment."""
    print_header("Verifying Environment")

    checks = []

    # Check .env file
    env_file = Path(".env")
    checks.append(("Config (.env)", env_file.exists()))

    # Check certificate files
    cert_file = Path("certs/certificate.crt")
    key_file = Path("certs/private.key")
    checks.append(("SSL Certificate", cert_file.exists()))
    checks.append(("SSL Private Key", key_file.exists()))

    # Print results
    all_good = True
    for check_name, status in checks:
        symbol = "✅" if status else "❌"
        print(f"  {symbol} {check_name}")
        if not status:
            all_good = False

    return all_good


def print_next_steps():
    """Print next steps."""
    print_header("Next Steps")
    print("""
HTTPS is now required for all environments.
SSL certificates are auto-generated on first run.

To start the development server:

   uv run python run.py

Or use uvicorn directly:
   uv run uvicorn app.app:app --reload \\
       --ssl-keyfile=./certs/private.key \\
       --ssl-certfile=./certs/certificate.crt

To view the API documentation:
   https://localhost:8000/docs

For Firefox/Chrome, you may need to accept the self-signed certificate.
Just navigate to https://localhost:8000 and click "Advanced" → "Proceed".

For production deployments:
   - Copy appropriate .env.production to .env
   - Replace ./certs/private.key and ./certs/certificate.crt with real certificates
   - Deploy to your server
""")


def main():
    """Main setup function."""
    print("\n" + "=" * 60)
    print("🔧 FastAPI Development Environment Setup")
    print("=" * 60)

    # Generate SSL certificates
    cert_ok = generate_ssl_certificates()

    # Create .env file
    env_ok = create_env_file()

    # Verify environment
    print()
    verify_ok = verify_environment()

    # Print results
    print("\n" + "=" * 60)
    if cert_ok and env_ok and verify_ok:
        print("✨ Development environment setup completed successfully!")
    else:
        print("⚠️  Some steps may need manual attention")
    print("=" * 60)

    # Print next steps
    print_next_steps()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
