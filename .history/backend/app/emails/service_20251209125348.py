"""Email service with multi-provider support."""

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
    Email service supporting multiple providers.

    Usage:
        # Send with default provider (from settings)
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
    def get_default_provider() -> EmailProvider:
        """Get default provider from settings."""
        try:
            return EmailProvider(settings.default_email_provider)
        except ValueError:
            return EmailProvider.RESEND

    @staticmethod
    def get_available_providers() -> list[EmailProvider]:
        """Get list of configured providers."""
        providers = []
        if settings.resend_api_key:
            providers.append(EmailProvider.RESEND)
        if settings.brevo_api_key:
            providers.append(EmailProvider.BREVO)
        return providers

    @staticmethod
    async def send(
        request: EmailRequest,
        provider: EmailProvider | None = None,
        fallback: bool = True,
    ) -> EmailResponse:
        """
        Send an email using the specified or default provider.

        Args:
            request: Email request with to, subject, content
            provider: Specific provider to use (optional)
            fallback: If True, try other providers if the first fails

        Returns:
            EmailResponse with success status and message_id
        """
        available = EmailService.get_available_providers()

        if not available:
            logger.error("No email providers configured")
            return EmailResponse(
                success=False,
                provider=EmailProvider.RESEND,
                error="No email providers configured",
            )

        # Determine which provider to use
        target = provider or EmailService.get_default_provider()

        # If target not available, use first available
        if target not in available:
            target = available[0]
            logger.warning(f"Requested provider not available, using {target}")

        # Send with target provider
        response = await EmailService._send_with_provider(request, target)

        # Fallback to other providers if failed
        if fallback and not response.success:
            for fallback_provider in available:
                if fallback_provider != target:
                    logger.info(f"Falling back to {fallback_provider}")
                    response = await EmailService._send_with_provider(request, fallback_provider)
                    if response.success:
                        break

        return response

    @staticmethod
    async def _send_with_provider(request: EmailRequest, provider: EmailProvider) -> EmailResponse:
        """Send email with specific provider."""
        if provider == EmailProvider.RESEND:
            return await ResendProvider.send(request)
        elif provider == EmailProvider.BREVO:
            return await BrevoProvider.send(request)
        else:
            return EmailResponse(
                success=False,
                provider=provider,
                error=f"Unknown provider: {provider}",
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

    @staticmethod
    async def health_check() -> dict[EmailProvider, bool]:
        """Check health of all configured providers."""
        results = {}
        if settings.resend_api_key:
            results[EmailProvider.RESEND] = await ResendProvider.health_check()
        if settings.brevo_api_key:
            results[EmailProvider.BREVO] = await BrevoProvider.health_check()
        return results


# Convenience functions
async def send_email(
    to: str,
    subject: str,
    html_content: str,
    text_content: str | None = None,
    provider: EmailProvider | None = None,
) -> EmailResponse:
    """Send an email (convenience function)."""
    request = EmailRequest(
        to=to,
        subject=subject,
        html_content=html_content,
        text_content=text_content,
    )
    return await EmailService.send(request, provider=provider)


async def send_welcome_email(to: str, name: str, dashboard_url: str = "") -> EmailResponse:
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
