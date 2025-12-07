"""Email service for sending login codes."""

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

from app.config.logger import get_logger
from app.config.settings import get_settings

logger = get_logger(__name__)


class MailService:
    """Service for sending emails via SMTP."""

    def __init__(self):
        """Initialize mail service with settings."""
        self.settings = get_settings()
        self._mail_config: ConnectionConfig | None = None

    def _get_mail_config(self) -> ConnectionConfig:
        """Get or create mail configuration.

        Returns:
            FastMail connection configuration
        """
        if self._mail_config is None:
            # ConnectionConfig expects uppercase MAIL_* environment variables
            # It reads from environment, so we need to map our settings
            self._mail_config = ConnectionConfig(
                MAIL_USERNAME=self.settings.mail_username,
                MAIL_PASSWORD=self.settings.mail_password,
                MAIL_FROM=self.settings.mail_from,
                MAIL_PORT=self.settings.mail_port,
                MAIL_SERVER=self.settings.mail_server,
                MAIL_STARTTLS=self.settings.mail_starttls,
                MAIL_SSL_TLS=self.settings.mail_ssl,
            )
        return self._mail_config

    async def send_login_code_email(self, email: str, code: str) -> bool:
        """Send login code to email via SMTP.

        Args:
            email: Recipient email address
            code: Login code to send

        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            subject = "Your Login Code"
            body = self._generate_login_code_body(code)
            html_body = self._generate_login_code_html(code)

            return await self.send_email(
                to=email, subject=subject, body=body, html=html_body
            )

        except Exception as e:
            logger.error(f"Failed to send login code email to {email}: {str(e)}")
            return False

    def _generate_login_code_body(self, code: str) -> str:
        """Generate plain text email body for login code.

        Args:
            code: Login code

        Returns:
            Plain text email body
        """
        expiry_minutes = self.settings.login_code_expiry_minutes
        return f"""Your Login Code

Your secure login code is:

    {code}

This code will expire in {expiry_minutes} minutes.

Do not share this code with anyone.

If you didn't request this code, please ignore this email."""

    def _generate_login_code_html(self, code: str) -> str:
        """Generate HTML email body for login code.

        Args:
            code: Login code

        Returns:
            HTML email body
        """
        expiry_minutes = self.settings.login_code_expiry_minutes
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50;">Your Login Code</h2>

                    <p>Your secure login code is:</p>

                    <div style="background-color: #f5f5f5; padding: 20px;
                                border-radius: 5px; text-align: center;
                                margin: 20px 0;">
                        <span style="font-size: 32px; font-weight: bold;
                                   letter-spacing: 5px; color: #2980b9;">
                            {code}
                        </span>
                    </div>

                    <p>This code will expire in <strong>{expiry_minutes}
                    minutes</strong>.</p>

                    <p style="color: #e74c3c; font-weight: bold;">Do not share
                    this code with anyone.</p>

                    <p style="color: #7f8c8d; font-size: 12px;">
                        If you didn't request this code, please ignore this
                        email.
                    </p>
                </div>
            </body>
        </html>
        """

    async def send_email(
        self, to: str, subject: str, body: str, html: str | None = None
    ) -> bool:
        """Send a generic email via SMTP.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            html: Optional HTML version

        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            # Check if mail credentials are configured
            if not self.settings.mail_username:
                logger.warning(
                    "Mail credentials not configured (MAIL_USERNAME not set). "
                    "Email not sent. Configure .env with valid SMTP settings."
                )
                return False

            config = self._get_mail_config()
            message = MessageSchema(
                subject=subject,
                recipients=[to],
                body=body,
                subtype="plain",
                html=html,
            )

            fm = FastMail(config)
            await fm.send_message(message)

            logger.info(f"Email sent to: {to} | Subject: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to}: {str(e)}")
            return False
