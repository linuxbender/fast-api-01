"""
SSL Certificate Generator for Local Development

This module provides utilities to generate self-signed SSL certificates
for local development environments.

Usage:
    uv run python -m app.config.ssl_generator
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

try:
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
except ImportError:
    print("❌ Error: cryptography module not installed")
    print("   Install it with: uv add --dev cryptography")
    sys.exit(1)


class SSLCertificateGenerator:
    """Generate self-signed SSL certificates for development."""

    def __init__(self, cert_dir: str = "./certs"):
        """Initialize certificate generator.
        
        Args:
            cert_dir: Directory to store certificates
        """
        self.cert_dir = Path(cert_dir)
        self.cert_file = self.cert_dir / "certificate.crt"
        self.key_file = self.cert_dir / "private.key"

    def create_certificate_directory(self) -> None:
        """Create certificate directory if it doesn't exist."""
        self.cert_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Certificate directory ready: {self.cert_dir.absolute()}")

    def generate_private_key(self) -> rsa.RSAPrivateKey:
        """Generate RSA private key.
        
        Returns:
            RSA private key
        """
        print("🔐 Generating RSA private key (2048 bits)...")
        return rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend(),
        )

    def generate_self_signed_cert(
        self,
        private_key: rsa.RSAPrivateKey,
        days_valid: int = 365,
    ) -> x509.Certificate:
        """Generate self-signed certificate.
        
        Args:
            private_key: RSA private key
            days_valid: Number of days certificate is valid
            
        Returns:
            Self-signed certificate
        """
        print(f"📝 Generating self-signed certificate (valid for {days_valid} days)...")

        subject = issuer = x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, "DE"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Bavaria"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Local"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "FastAPI Dev"),
                x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
            ]
        )

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=days_valid))
            .add_extension(
                x509.SubjectAlternativeName(
                    [
                        x509.DNSName("localhost"),
                        x509.DNSName("*.localhost"),
                        x509.DNSName("127.0.0.1"),
                    ]
                ),
                critical=False,
            )
            .sign(private_key, hashes.SHA256(), default_backend())
        )

        return cert

    def save_private_key(self, private_key: rsa.RSAPrivateKey) -> None:
        """Save private key to file.
        
        Args:
            private_key: RSA private key to save
        """
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
        self.key_file.write_bytes(pem)
        self.key_file.chmod(0o600)  # Read/write for owner only
        print(f"✅ Private key saved: {self.key_file.absolute()}")

    def save_certificate(self, cert: x509.Certificate) -> None:
        """Save certificate to file.
        
        Args:
            cert: Certificate to save
        """
        pem = cert.public_bytes(serialization.Encoding.PEM)
        self.cert_file.write_bytes(pem)
        print(f"✅ Certificate saved: {self.cert_file.absolute()}")

    def display_cert_info(self, cert: x509.Certificate) -> None:
        """Display certificate information.
        
        Args:
            cert: Certificate to display info for
        """
        print("\n" + "=" * 60)
        print("📜 Certificate Information")
        print("=" * 60)
        print(f"Subject: {cert.subject.rfc4514_string()}")
        print(f"Issuer: {cert.issuer.rfc4514_string()}")
        print(f"Serial Number: {cert.serial_number}")
        print(f"Not Before: {cert.not_valid_before}")
        print(f"Not After: {cert.not_valid_after}")
        print(f"Valid Days: {(cert.not_valid_after - cert.not_valid_before).days}")
        print("=" * 60 + "\n")

    def generate(self, days_valid: int = 365, force: bool = False) -> bool:
        """Generate self-signed certificate.
        
        Args:
            days_valid: Number of days certificate should be valid
            force: Overwrite existing certificates
            
        Returns:
            True if successful
        """
        # Check if certificates already exist
        if self.cert_file.exists() and self.key_file.exists() and not force:
            print("⚠️  Certificates already exist!")
            print(f"   Key: {self.key_file.absolute()}")
            print(f"   Cert: {self.cert_file.absolute()}")
            print("   Use --force to regenerate")
            return False

        try:
            # Create directory
            self.create_certificate_directory()

            # Generate private key
            private_key = self.generate_private_key()

            # Generate self-signed certificate
            cert = self.generate_self_signed_cert(private_key, days_valid)

            # Save files
            self.save_private_key(private_key)
            self.save_certificate(cert)

            # Display info
            self.display_cert_info(cert)

            print("✨ SSL certificate generation completed successfully!")
            return True

        except Exception as e:
            print(f"❌ Error generating certificate: {e}")
            return False


def main():
    """Main entry point for certificate generation."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate self-signed SSL certificates for development"
    )
    parser.add_argument(
        "--cert-dir",
        default="./certs",
        help="Directory to store certificates (default: ./certs)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=365,
        help="Number of days certificate is valid (default: 365)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing certificates",
    )

    args = parser.parse_args()

    generator = SSLCertificateGenerator(cert_dir=args.cert_dir)
    success = generator.generate(days_valid=args.days, force=args.force)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
