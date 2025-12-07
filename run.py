#!/usr/bin/env python3
"""
FastAPI Application Runner with Required HTTPS Support

This script starts the FastAPI server with HTTPS support.
SSL certificates are auto-generated if they don't exist.

Usage:
    uv run python run.py
    uv run python run.py --port 9000
    uv run python run.py --help
"""

import argparse
import sys
from pathlib import Path

try:
    import uvicorn
except ImportError:
    print("❌ Error: uvicorn not installed")
    sys.exit(1)

from app.config.logger import get_logger
from app.config.settings import get_settings, has_ssl_certificates
from app.config.ssl_generator import SSLCertificateGenerator

logger = get_logger(__name__)


def main():
    """Main entry point for running the FastAPI server."""
    parser = argparse.ArgumentParser(
        description="Run FastAPI server with optional HTTPS support"
    )
    parser.add_argument(
        "--host",
        default=None,
        help="Server host (overrides config)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Server port (overrides config)",
    )
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Disable auto-reload",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes",
    )

    args = parser.parse_args()

    # Load settings from environment
    settings = get_settings()

    # Determine host and port
    host = args.host or settings.server_host
    port = args.port or settings.server_port
    reload = not args.no_reload and settings.server_reload

    # HTTPS is always required
    # Auto-generate certificates if they don't exist
    if not has_ssl_certificates():
        logger.info("SSL certificates not found, generating self-signed certificates...")
        cert_dir = str(Path(settings.ssl_keyfile).parent)
        generator = SSLCertificateGenerator(cert_dir=cert_dir)
        generator.create_certificate_directory()
        generator.generate(days_valid=365)
        logger.info(f"✅ Self-signed certificates generated in {generator.cert_dir}")

    ssl_keyfile = settings.ssl_keyfile
    ssl_certfile = settings.ssl_certfile
    protocol = "https"

    print("\n" + "=" * 60)
    print("🚀 Starting FastAPI Server (HTTPS)")
    print("=" * 60)
    print(f"Environment: {settings.environment}")
    print(f"URL: {protocol}://{host}:{port}")
    print(f"Reload: {reload}")
    print(f"SSL Key: {Path(ssl_keyfile).absolute()}")
    print(f"SSL Cert: {Path(ssl_certfile).absolute()}")
    print("=" * 60 + "\n")

    logger.info(f"Starting server: {protocol}://{host}:{port}")

    # Start the server
    try:
        uvicorn.run(
            "app.app:app",
            host=host,
            port=port,
            reload=reload,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
            workers=args.workers,
        )
    except KeyboardInterrupt:
        print("\n\n👋 Server shutdown by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        print(f"❌ Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
