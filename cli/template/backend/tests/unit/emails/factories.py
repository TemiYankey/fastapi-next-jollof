"""Test factories for email module."""

from contextlib import contextmanager
from unittest.mock import patch

from app.core.config import settings
from app.emails.enums import EmailProvider, EmailType
from app.emails.schemas import EmailRequest, EmailResponse, TemplatedEmailRequest


class SettingsFactory:
    """Factory for mocking settings in tests."""

    DEFAULT_SETTINGS = {
        "resend_api_key": "re_test_key",
        "brevo_api_key": "xkeysib_test_key",
        "from_email": "test@example.com",
        "from_name": "Test App",
        "app_name": "Test App",
        "default_email_provider": "resend",
        "primary_color": "#6366f1",
    }

    @classmethod
    @contextmanager
    def mock(cls, **overrides):
        """
        Context manager to mock settings with defaults.

        Usage:
            with SettingsFactory.mock():
                # settings are mocked with defaults

            with SettingsFactory.mock(resend_api_key=""):
                # settings with empty resend key
        """
        values = {**cls.DEFAULT_SETTINGS, **overrides}
        patches = [
            patch.object(settings, key, value)
            for key, value in values.items()
        ]

        for p in patches:
            p.start()
        try:
            yield settings
        finally:
            for p in patches:
                p.stop()


class EmailRequestFactory:
    """Factory for creating EmailRequest test objects."""

    @staticmethod
    def create(
        to: str = "recipient@example.com",
        subject: str = "Test Subject",
        html_content: str = "<p>Test HTML content</p>",
        text_content: str | None = "Test text content",
        from_email: str | None = None,
        from_name: str | None = None,
        reply_to: str | None = None,
    ) -> EmailRequest:
        """Create an EmailRequest with defaults."""
        return EmailRequest(
            to=to,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            from_email=from_email,
            from_name=from_name,
            reply_to=reply_to,
        )

    @staticmethod
    def create_with_custom_from(
        from_email: str = "custom@example.com",
        from_name: str = "Custom Sender",
    ) -> EmailRequest:
        """Create an EmailRequest with custom from address."""
        return EmailRequestFactory.create(
            from_email=from_email,
            from_name=from_name,
        )

    @staticmethod
    def create_with_reply_to(reply_to: str = "reply@example.com") -> EmailRequest:
        """Create an EmailRequest with reply-to address."""
        return EmailRequestFactory.create(reply_to=reply_to)


class TemplatedEmailRequestFactory:
    """Factory for creating TemplatedEmailRequest test objects."""

    @staticmethod
    def create(
        to: str = "recipient@example.com",
        email_type: EmailType = EmailType.WELCOME,
        context: dict | None = None,
        from_email: str | None = None,
        from_name: str | None = None,
        reply_to: str | None = None,
    ) -> TemplatedEmailRequest:
        """Create a TemplatedEmailRequest with defaults."""
        return TemplatedEmailRequest(
            to=to,
            email_type=email_type,
            context=context or {},
            from_email=from_email,
            from_name=from_name,
            reply_to=reply_to,
        )

    @staticmethod
    def create_welcome(
        to: str = "recipient@example.com",
        name: str = "Test User",
    ) -> TemplatedEmailRequest:
        """Create a welcome email request."""
        return TemplatedEmailRequestFactory.create(
            to=to,
            email_type=EmailType.WELCOME,
            context={"name": name},
        )

    @staticmethod
    def create_password_reset(
        to: str = "recipient@example.com",
        reset_url: str = "https://example.com/reset",
    ) -> TemplatedEmailRequest:
        """Create a password reset email request."""
        return TemplatedEmailRequestFactory.create(
            to=to,
            email_type=EmailType.PASSWORD_RESET,
            context={"reset_url": reset_url},
        )


class EmailResponseFactory:
    """Factory for creating EmailResponse test objects."""

    @staticmethod
    def create_success(
        provider: EmailProvider = EmailProvider.RESEND,
        message_id: str = "test-message-id-123",
    ) -> EmailResponse:
        """Create a successful EmailResponse."""
        return EmailResponse(
            success=True,
            provider=provider,
            message_id=message_id,
            error=None,
        )

    @staticmethod
    def create_failure(
        provider: EmailProvider = EmailProvider.RESEND,
        error: str = "Test error message",
    ) -> EmailResponse:
        """Create a failed EmailResponse."""
        return EmailResponse(
            success=False,
            provider=provider,
            message_id=None,
            error=error,
        )

    @staticmethod
    def create_resend_success(message_id: str = "resend-id-123") -> EmailResponse:
        """Create a successful Resend response."""
        return EmailResponseFactory.create_success(
            provider=EmailProvider.RESEND,
            message_id=message_id,
        )

    @staticmethod
    def create_brevo_success(message_id: str = "brevo-id-123") -> EmailResponse:
        """Create a successful Brevo response."""
        return EmailResponseFactory.create_success(
            provider=EmailProvider.BREVO,
            message_id=message_id,
        )
