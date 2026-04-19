"""Tests for EmailService."""

from unittest.mock import patch

import pytest

from app.emails.enums import EmailProvider, EmailType
from app.emails.schemas import EmailResponse
from app.emails.service import (
    EmailService,
    send_email,
    send_password_reset_email,
    send_payment_success_email,
    send_verification_email,
    send_welcome_email,
)

from .factories import (
    EmailRequestFactory,
    EmailResponseFactory,
    SettingsFactory,
    TemplatedEmailRequestFactory,
)


class TestEmailService:
    """Tests for EmailService class."""

    @pytest.mark.asyncio
    async def test_send_with_resend_provider(self):
        """Test send uses Resend provider."""
        email_request = EmailRequestFactory.create()
        mock_response = EmailResponseFactory.create_resend_success()

        with SettingsFactory.mock(default_email_provider="resend"):
            with patch(
                "app.emails.service.ResendProvider.send", return_value=mock_response
            ) as mock_resend:
                response = await EmailService.send(
                    email_request, provider=EmailProvider.RESEND
                )

                assert response.success is True
                mock_resend.assert_called_once_with(email_request)

    @pytest.mark.asyncio
    async def test_send_with_brevo_provider(self):
        """Test send uses Brevo provider."""
        email_request = EmailRequestFactory.create()
        mock_response = EmailResponseFactory.create_brevo_success()

        with SettingsFactory.mock(default_email_provider="brevo"):
            with patch(
                "app.emails.service.BrevoProvider.send", return_value=mock_response
            ) as mock_brevo:
                response = await EmailService.send(
                    email_request, provider=EmailProvider.BREVO
                )

                assert response.success is True
                mock_brevo.assert_called_once_with(email_request)

    @pytest.mark.asyncio
    async def test_send_uses_default_provider_from_settings(self):
        """Test send uses default provider from settings."""
        email_request = EmailRequestFactory.create()
        mock_response = EmailResponseFactory.create_resend_success()

        with SettingsFactory.mock(default_email_provider="resend"):
            with patch(
                "app.emails.service.ResendProvider.send", return_value=mock_response
            ) as mock_resend:
                response = await EmailService.send(email_request)

                assert response.success is True
                mock_resend.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_with_unknown_provider(self):
        """Test send raises error for unknown provider."""
        email_request = EmailRequestFactory.create()

        with SettingsFactory.mock(default_email_provider="unknown"):
            with pytest.raises(ValueError, match="is not a valid EmailProvider"):
                await EmailService.send(email_request)

    @pytest.mark.asyncio
    async def test_send_templated(self):
        """Test send_templated generates template and sends."""
        request = TemplatedEmailRequestFactory.create_welcome(name="John")
        mock_response = EmailResponseFactory.create_resend_success()

        with SettingsFactory.mock():
            with patch.object(EmailService, "send", return_value=mock_response) as mock_send:
                response = await EmailService.send_templated(request)

                assert response.success is True
                mock_send.assert_called_once()

                # Verify EmailRequest was created from template
                call_args = mock_send.call_args
                email_request = call_args[0][0]
                assert email_request.to == "recipient@example.com"
                assert "Welcome" in email_request.subject
                assert "John" in email_request.html_content


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    @pytest.mark.asyncio
    async def test_send_email(self):
        """Test send_email convenience function."""
        mock_response = EmailResponseFactory.create_resend_success()

        with SettingsFactory.mock():
            with patch.object(EmailService, "send", return_value=mock_response) as mock_send:
                response = await send_email(
                    to="test@example.com",
                    subject="Test Subject",
                    html_content="<p>Content</p>",
                )

                assert response.success is True
                mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_welcome_email(self):
        """Test send_welcome_email convenience function."""
        mock_response = EmailResponseFactory.create_resend_success()

        with SettingsFactory.mock():
            with patch.object(
                EmailService, "send_templated", return_value=mock_response
            ) as mock_send:
                response = await send_welcome_email(
                    to="test@example.com",
                    name="John Doe",
                    dashboard_url="https://example.com/dashboard",
                )

                assert response.success is True
                call_args = mock_send.call_args
                request = call_args[0][0]
                assert request.email_type == EmailType.WELCOME
                assert request.context["name"] == "John Doe"

    @pytest.mark.asyncio
    async def test_send_password_reset_email(self):
        """Test send_password_reset_email convenience function."""
        mock_response = EmailResponseFactory.create_resend_success()

        with SettingsFactory.mock():
            with patch.object(
                EmailService, "send_templated", return_value=mock_response
            ) as mock_send:
                response = await send_password_reset_email(
                    to="test@example.com",
                    reset_url="https://example.com/reset?token=abc",
                )

                assert response.success is True
                call_args = mock_send.call_args
                request = call_args[0][0]
                assert request.email_type == EmailType.PASSWORD_RESET
                assert "token=abc" in request.context["reset_url"]

    @pytest.mark.asyncio
    async def test_send_verification_email(self):
        """Test send_verification_email convenience function."""
        mock_response = EmailResponseFactory.create_resend_success()

        with SettingsFactory.mock():
            with patch.object(
                EmailService, "send_templated", return_value=mock_response
            ) as mock_send:
                response = await send_verification_email(
                    to="test@example.com",
                    verify_url="https://example.com/verify?token=xyz",
                )

                assert response.success is True
                call_args = mock_send.call_args
                request = call_args[0][0]
                assert request.email_type == EmailType.EMAIL_VERIFICATION

    @pytest.mark.asyncio
    async def test_send_payment_success_email(self):
        """Test send_payment_success_email convenience function."""
        mock_response = EmailResponseFactory.create_resend_success()

        with SettingsFactory.mock():
            with patch.object(
                EmailService, "send_templated", return_value=mock_response
            ) as mock_send:
                response = await send_payment_success_email(
                    to="test@example.com",
                    amount="₦5,000",
                    credits="50",
                    reference="PAY-123",
                    dashboard_url="https://example.com/dashboard",
                )

                assert response.success is True
                call_args = mock_send.call_args
                request = call_args[0][0]
                assert request.email_type == EmailType.PAYMENT_SUCCESS
                assert request.context["amount"] == "₦5,000"
                assert request.context["credits"] == "50"
                assert request.context["reference"] == "PAY-123"
