"""Test factories for email tests."""

from contextlib import contextmanager
from unittest.mock import patch

from app.emails.schemas import EmailRequest


class EmailRequestFactory:
    """Factory for creating EmailRequest test objects."""

    @staticmethod
    def create(
        to: str = "test@example.com",
        subject: str = "Test Subject",
        html_content: str = "<p>Test content</p>",
        text_content: str = "Test content",
    ) -> EmailRequest:
        """Create a basic email request."""
        return EmailRequest(
            to=to,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
        )

    @staticmethod
    def create_with_custom_from() -> EmailRequest:
        """Create email request with custom from address."""
        return EmailRequest(
            to="test@example.com",
            subject="Test",
            html_content="<p>Test</p>",
            from_email="custom@example.com",
            from_name="Custom Sender",
        )

    @staticmethod
    def create_with_reply_to() -> EmailRequest:
        """Create email request with reply-to."""
        return EmailRequest(
            to="test@example.com",
            subject="Test",
            html_content="<p>Test</p>",
            reply_to="reply@example.com",
        )


class SettingsFactory:
    """Factory for mocking settings in tests."""

    @staticmethod
    @contextmanager
    def mock(
        resend_api_key: str = "re_test_key",
        from_email: str = "test@example.com",
        from_name: str = "Test App",
        app_name: str = "Test App",
        primary_color: str = "#6366f1",
    ):
        """Context manager to mock settings."""
        # Need to patch settings in all modules that import it
        with patch("app.emails.service.settings") as mock_service_settings, \
             patch("app.emails.templates.settings") as mock_template_settings, \
             patch("app.emails.providers.resend.settings") as mock_provider_settings:
            mock_service_settings.resend_api_key = resend_api_key
            mock_provider_settings.resend_api_key = resend_api_key
            # Set common settings on all mock objects
            for mock_settings in [mock_service_settings, mock_template_settings, mock_provider_settings]:
                mock_settings.from_email = from_email
                mock_settings.from_name = from_name
                mock_settings.app_name = app_name
                mock_settings.primary_color = primary_color
            yield mock_service_settings
