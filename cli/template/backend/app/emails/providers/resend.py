"""Resend email provider using official SDK."""

import asyncio

import resend

from app.core.config import settings
from app.core.logger import get_email_logger
from app.emails.enums import EmailProvider
from app.emails.schemas import EmailRequest, EmailResponse

logger = get_email_logger("resend")


class ResendProvider:
    """Resend email provider using official SDK."""

    provider = EmailProvider.RESEND

    @staticmethod
    async def send(
        request: EmailRequest,
        attachment_content: bytes | None = None,
        attachment_filename: str | None = None,
    ) -> EmailResponse:
        """
        Send email via Resend SDK.

        Args:
            request: Email request
            attachment_content: Optional attachment bytes
            attachment_filename: Optional attachment filename

        Returns:
            EmailResponse with success status
        """
        try:
            # Set API key from settings
            resend.api_key = settings.resend_api_key

            # Get from address - use request values or fall back to settings
            from_email = request.from_email or settings.from_email
            from_name = request.from_name or settings.from_name
            from_address = f"{from_name} <{from_email}>"

            # Build params using SDK types
            params: resend.Emails.SendParams = {
                "from": from_address,
                "to": [request.to],
                "subject": request.subject,
                "html": request.html_content,
            }

            # Add text content if provided
            if request.text_content:
                params["text"] = request.text_content

            # Add reply-to if provided
            if request.reply_to:
                params["reply_to"] = request.reply_to

            # Add attachment if provided
            if attachment_content and attachment_filename:
                params["attachments"] = [
                    {
                        "filename": attachment_filename,
                        "content": list(attachment_content),
                    }
                ]
                logger.debug(
                    f"Adding attachment: {attachment_filename} ({len(attachment_content)} bytes)"
                )

            logger.info(f"Sending email via Resend from: {from_email} to: {request.to}")

            # Run sync SDK call in thread pool to not block event loop
            email = await asyncio.to_thread(resend.Emails.send, params)

            message_id = email.get("id") if isinstance(email, dict) else getattr(email, "id", None)
            logger.info(f"Email sent successfully via Resend - ID: {message_id}")

            return EmailResponse(
                success=True,
                message_id=message_id,
                provider=EmailProvider.RESEND,
            )

        except resend.exceptions.ResendError as e:
            error_msg = str(e)
            logger.error(f"Resend SDK error: {error_msg}")
            return EmailResponse(
                success=False,
                provider=EmailProvider.RESEND,
                error=f"Resend Error: {error_msg}",
            )
        except Exception as e:
            logger.error(f"Resend send error: {str(e)}")
            return EmailResponse(
                success=False,
                provider=EmailProvider.RESEND,
                error=str(e),
            )

    @staticmethod
    async def health_check() -> bool:
        """Check Resend API connectivity by fetching domains."""
        if not settings.resend_api_key:
            return False

        try:
            resend.api_key = settings.resend_api_key
            await asyncio.to_thread(resend.Domains.list)
            return True
        except Exception as e:
            logger.warning(f"Resend health check failed: {e}")
            return False
