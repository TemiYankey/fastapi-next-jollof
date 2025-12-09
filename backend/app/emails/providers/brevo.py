"""Brevo (formerly Sendinblue) email provider - tested implementation from Writera."""

import base64

import httpx

from app.core.config import settings
from app.core.logger import get_email_logger
from app.emails.enums import EmailProvider
from app.emails.schemas import EmailRequest, EmailResponse

logger = get_email_logger("brevo")


class BrevoProvider:
    """Brevo email provider - tested implementation from Writera."""

    provider = EmailProvider.BREVO

    @staticmethod
    async def send(
        request: EmailRequest,
        attachment_content: bytes | None = None,
        attachment_filename: str | None = None,
    ) -> EmailResponse:
        """
        Send email via Brevo API - tested implementation from Writera.

        Args:
            request: Email request
            attachment_content: Optional attachment bytes (e.g., PDF)
            attachment_filename: Optional attachment filename

        Returns:
            EmailResponse with success status
        """
        try:
            # Get from address - use request values or fall back to settings
            sender_email = request.from_email or settings.from_email
            sender_name = request.from_name or settings.from_name

            # Simple JSON payload - exact pattern from Writera
            payload = {
                "sender": {"name": sender_name, "email": sender_email},
                "to": [{"email": request.to}],
                "subject": request.subject,
                "htmlContent": request.html_content,
            }

            # Add attachment if provided
            if attachment_content and attachment_filename:
                encoded_content = base64.b64encode(attachment_content).decode()
                payload["attachment"] = [
                    {"content": encoded_content, "name": attachment_filename}
                ]
                logger.debug(
                    f"Adding attachment: {attachment_filename} ({len(attachment_content)} bytes)"
                )

            logger.info(f"Sending email via Brevo from: {sender_email} to: {request.to}")
            logger.debug(
                f"Email details: subject='{request.subject}' ({len(request.html_content)} chars HTML)"
            )

            # Make HTTP request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.brevo.com/v3/smtp/email",
                    json=payload,
                    headers={
                        "accept": "application/json",
                        "api-key": settings.brevo_api_key,
                        "content-type": "application/json",
                    },
                    timeout=30.0,
                )

            # Check response - Brevo returns 201 on success
            if response.status_code == 201:
                data = response.json()
                message_id = data.get("messageId", "unknown")
                logger.info(f"Email sent successfully via Brevo - MessageId: {message_id}")
                return EmailResponse(
                    success=True,
                    message_id=message_id,
                    provider=EmailProvider.BREVO,
                )
            else:
                error_msg = f"Brevo API returned {response.status_code}: {response.text}"
                logger.error(error_msg)
                return EmailResponse(
                    success=False,
                    provider=EmailProvider.BREVO,
                    error=error_msg,
                )

        except httpx.TimeoutException:
            logger.error("Brevo API timeout")
            return EmailResponse(
                success=False,
                provider=EmailProvider.BREVO,
                error="Request timeout",
            )
        except Exception as e:
            logger.error(f"Brevo API error: {str(e)}")
            return EmailResponse(
                success=False,
                provider=EmailProvider.BREVO,
                error=f"Brevo Error: {str(e)}",
            )

    @staticmethod
    async def health_check() -> bool:
        """Check Brevo API connectivity."""
        if not settings.brevo_api_key:
            return False

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.brevo.com/v3/account",
                    headers={
                        "accept": "application/json",
                        "api-key": settings.brevo_api_key,
                    },
                    timeout=10.0,
                )
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"Brevo health check failed: {e}")
            return False
