"""Email service."""

from app.core.config import settings
from app.core.logger import get_email_logger
from app.emails.enums import EmailProvider, EmailType
from app.emails.providers.brevo import BrevoProvider
from app.emails.providers.resend import ResendProvider
from app.emails.schemas import EmailRequest, EmailResponse, TemplatedEmailRequest
from app.emails.templates import get_email_template

logger = get_email_logger()


class EmailService:
    """
    Email service.

    Usage:
        # Send with default provider (from settings.default_email_provider)
        await EmailService.send(EmailRequest(...))

        # Send with specific provider
        await EmailService.send(EmailRequest(...), provider=EmailProvider.BREVO)

        # Send templated email
        await EmailService.send_templated(TemplatedEmailRequest(
            to="user@example.com",
            email_type=EmailType.WELCOME,
            context={"name": "John"}
        ))
    """

    @staticmethod
    async def send(
        request: EmailRequest,
        provider: EmailProvider | None = None,
    ) -> EmailResponse:
        """
        Send an email using the specified or default provider.

        Args:
            request: Email request with to, subject, content
            provider: Specific provider to use (defaults to settings.default_email_provider)

        Returns:
            EmailResponse with success status and message_id
        """
        target = provider or EmailProvider(settings.default_email_provider)

        if target == EmailProvider.RESEND:
            return await ResendProvider.send(request)
        elif target == EmailProvider.BREVO:
            return await BrevoProvider.send(request)
        else:
            logger.error(f"Unknown email provider: {target}")
            return EmailResponse(
                success=False,
                provider=target,
                error=f"Unknown provider: {target}",
            )

    @staticmethod
    async def send_templated(
        request: TemplatedEmailRequest,
        provider: EmailProvider | None = None,
    ) -> EmailResponse:
        """
        Send a templated email.

        Args:
            request: Templated email request with email_type and context
            provider: Specific provider to use (optional)

        Returns:
            EmailResponse
        """
        subject, html_content, text_content = get_email_template(
            request.email_type, request.context
        )

        email_request = EmailRequest(
            to=request.to,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            from_email=request.from_email,
            from_name=request.from_name,
            reply_to=request.reply_to,
        )

        return await EmailService.send(email_request, provider=provider)


# Convenience functions
async def send_email(
    to: str,
    subject: str,
    html_content: str,
    text_content: str | None = None,
    provider: EmailProvider | None = None,
) -> EmailResponse:
    """Send an email."""
    request = EmailRequest(
        to=to,
        subject=subject,
        html_content=html_content,
        text_content=text_content,
    )
    return await EmailService.send(request, provider=provider)


async def send_welcome_email(
    to: str, name: str, dashboard_url: str = ""
) -> EmailResponse:
    """Send welcome email to new user."""
    request = TemplatedEmailRequest(
        to=to,
        email_type=EmailType.WELCOME,
        context={"name": name, "dashboard_url": dashboard_url},
    )
    return await EmailService.send_templated(request)


async def send_password_reset_email(to: str, reset_url: str) -> EmailResponse:
    """Send password reset email."""
    request = TemplatedEmailRequest(
        to=to,
        email_type=EmailType.PASSWORD_RESET,
        context={"reset_url": reset_url},
    )
    return await EmailService.send_templated(request)


async def send_verification_email(to: str, verify_url: str) -> EmailResponse:
    """Send email verification."""
    request = TemplatedEmailRequest(
        to=to,
        email_type=EmailType.EMAIL_VERIFICATION,
        context={"verify_url": verify_url},
    )
    return await EmailService.send_templated(request)


async def send_payment_success_email(
    to: str,
    amount: str,
    credits: str,
    reference: str,
    dashboard_url: str = "",
) -> EmailResponse:
    """Send payment success email."""
    request = TemplatedEmailRequest(
        to=to,
        email_type=EmailType.PAYMENT_SUCCESS,
        context={
            "amount": amount,
            "credits": credits,
            "reference": reference,
            "dashboard_url": dashboard_url,
        },
    )
    return await EmailService.send_templated(request)
