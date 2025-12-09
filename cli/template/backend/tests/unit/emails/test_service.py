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

    def test_get_default_provider_resend(self):
        """Test default provider is Resend."""
        with SettingsFactory.mock():
            provider = EmailService.get_default_provider()
            assert provider == EmailProvider.RESEND

    def test_get_default_provider_brevo(self):
        """Test default provider when set to Brevo."""
        with SettingsFactory.mock(default_email_provider="brevo"):
            provider = EmailService.get_default_provider()
            assert provider == EmailProvider.BREVO

    def test_get_default_provider_invalid_fallback(self):
        """Test fallback to Resend when invalid provider configured."""
        with SettingsFactory.mock(default_email_provider="invalid_provider"):
            provider = EmailService.get_default_provider()
            assert provider == EmailProvider.RESEND

    def test_get_available_providers_both(self):
        """Test both providers available."""
        with SettingsFactory.mock():
            providers = EmailService.get_available_providers()

            assert EmailProvider.RESEND in providers
            assert EmailProvider.BREVO in providers

    def test_get_available_providers_resend_only(self):
        """Test only Resend available."""
        with SettingsFactory.mock(brevo_api_key=""):
            providers = EmailService.get_available_providers()

            assert EmailProvider.RESEND in providers
            assert EmailProvider.BREVO not in providers

    def test_get_available_providers_brevo_only(self):
        """Test only Brevo available."""
        with SettingsFactory.mock(resend_api_key=""):
            providers = EmailService.get_available_providers()

            assert EmailProvider.RESEND not in providers
            assert EmailProvider.BREVO in providers

    def test_get_available_providers_none(self):
        """Test no providers configured."""
        with SettingsFactory.mock(resend_api_key="", brevo_api_key=""):
            providers = EmailService.get_available_providers()

            assert len(providers) == 0

    @pytest.mark.asyncio
    async def test_send_no_providers_configured(self):
        """Test send fails gracefully when no providers configured."""
        email_request = EmailRequestFactory.create()

        with SettingsFactory.mock(resend_api_key="", brevo_api_key=""):
            response = await EmailService.send(email_request)

            assert response.success is False
            assert "No email providers configured" in response.error

    @pytest.mark.asyncio
    async def test_send_with_default_provider(self):
        """Test send uses default provider."""
        email_request = EmailRequestFactory.create()
        mock_response = EmailResponseFactory.create_resend_success()

        with SettingsFactory.mock():
            with patch.object(
                EmailService, "_send_with_provider", return_value=mock_response
            ) as mock_send:
                response = await EmailService.send(email_request)

                assert response.success is True
                mock_send.assert_called_once()
                call_args = mock_send.call_args
                assert call_args[0][1] == EmailProvider.RESEND

    @pytest.mark.asyncio
    async def test_send_with_specific_provider(self):
        """Test send with explicitly specified provider."""
        email_request = EmailRequestFactory.create()
        mock_response = EmailResponseFactory.create_brevo_success()

        with SettingsFactory.mock():
            with patch.object(
                EmailService, "_send_with_provider", return_value=mock_response
            ) as mock_send:
                response = await EmailService.send(
                    email_request, provider=EmailProvider.BREVO
                )

                assert response.success is True
                call_args = mock_send.call_args
                assert call_args[0][1] == EmailProvider.BREVO

    @pytest.mark.asyncio
    async def test_send_fallback_on_failure(self):
        """Test fallback to other provider on failure."""
        email_request = EmailRequestFactory.create()
        failed_response = EmailResponseFactory.create_failure(
            provider=EmailProvider.RESEND
        )
        success_response = EmailResponseFactory.create_brevo_success(
            message_id="fallback-id"
        )

        call_count = 0

        async def mock_send(request, provider):
            nonlocal call_count
            call_count += 1
            if provider == EmailProvider.RESEND:
                return failed_response
            return success_response

        with SettingsFactory.mock():
            with patch.object(EmailService, "_send_with_provider", side_effect=mock_send):
                response = await EmailService.send(email_request, fallback=True)

                assert response.success is True
                assert response.provider == EmailProvider.BREVO
                assert call_count == 2  # Both providers tried

    @pytest.mark.asyncio
    async def test_send_no_fallback(self):
        """Test no fallback when disabled."""
        email_request = EmailRequestFactory.create()
        failed_response = EmailResponseFactory.create_failure(
            provider=EmailProvider.RESEND
        )

        with SettingsFactory.mock():
            with patch.object(
                EmailService, "_send_with_provider", return_value=failed_response
            ) as mock_send:
                response = await EmailService.send(email_request, fallback=False)

                assert response.success is False
                assert mock_send.call_count == 1  # No fallback attempted

    @pytest.mark.asyncio
    async def test_send_with_provider_resend(self):
        """Test _send_with_provider calls ResendProvider."""
        email_request = EmailRequestFactory.create()
        mock_response = EmailResponseFactory.create_resend_success()

        with SettingsFactory.mock():
            with patch(
                "app.emails.service.ResendProvider.send", return_value=mock_response
            ) as mock_resend:
                response = await EmailService._send_with_provider(
                    email_request, EmailProvider.RESEND
                )

                assert response.success is True
                mock_resend.assert_called_once_with(email_request)

    @pytest.mark.asyncio
    async def test_send_with_provider_brevo(self):
        """Test _send_with_provider calls BrevoProvider."""
        email_request = EmailRequestFactory.create()
        mock_response = EmailResponseFactory.create_brevo_success()

        with SettingsFactory.mock():
            with patch(
                "app.emails.service.BrevoProvider.send", return_value=mock_response
            ) as mock_brevo:
                response = await EmailService._send_with_provider(
                    email_request, EmailProvider.BREVO
                )

                assert response.success is True
                mock_brevo.assert_called_once_with(email_request)

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

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check for all providers."""
        with SettingsFactory.mock():
            with patch(
                "app.emails.service.ResendProvider.health_check", return_value=True
            ) as mock_resend:
                with patch(
                    "app.emails.service.BrevoProvider.health_check", return_value=False
                ) as mock_brevo:
                    results = await EmailService.health_check()

                    assert results[EmailProvider.RESEND] is True
                    assert results[EmailProvider.BREVO] is False


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
