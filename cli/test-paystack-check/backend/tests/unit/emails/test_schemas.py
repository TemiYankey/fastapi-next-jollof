"""Tests for email schemas."""

import pytest
from pydantic import ValidationError

from app.emails.enums import EmailProvider, EmailType
from app.emails.schemas import (
    EmailProviderConfig,
    EmailRequest,
    EmailResponse,
    TemplatedEmailRequest,
)


class TestEmailRequest:
    """Tests for EmailRequest schema."""

    def test_valid_email_request(self):
        """Test creating valid email request."""
        request = EmailRequest(
            to="test@example.com",
            subject="Test Subject",
            html_content="<p>Test content</p>",
        )

        assert request.to == "test@example.com"
        assert request.subject == "Test Subject"
        assert request.html_content == "<p>Test content</p>"
        assert request.text_content is None
        assert request.from_email is None
        assert request.from_name is None
        assert request.reply_to is None

    def test_email_request_with_all_fields(self):
        """Test email request with all optional fields."""
        request = EmailRequest(
            to="test@example.com",
            subject="Test Subject",
            html_content="<p>Test content</p>",
            text_content="Test content",
            from_email="sender@example.com",
            from_name="Sender Name",
            reply_to="reply@example.com",
        )

        assert request.text_content == "Test content"
        assert request.from_email == "sender@example.com"
        assert request.from_name == "Sender Name"
        assert request.reply_to == "reply@example.com"

    def test_invalid_to_email(self):
        """Test validation fails for invalid to email."""
        with pytest.raises(ValidationError) as exc_info:
            EmailRequest(
                to="invalid-email",
                subject="Test",
                html_content="<p>Test</p>",
            )

        assert "to" in str(exc_info.value)

    def test_invalid_reply_to_email(self):
        """Test validation fails for invalid reply_to email."""
        with pytest.raises(ValidationError) as exc_info:
            EmailRequest(
                to="test@example.com",
                subject="Test",
                html_content="<p>Test</p>",
                reply_to="not-an-email",
            )

        assert "reply_to" in str(exc_info.value)


class TestTemplatedEmailRequest:
    """Tests for TemplatedEmailRequest schema."""

    def test_valid_templated_request(self):
        """Test creating valid templated email request."""
        request = TemplatedEmailRequest(
            to="test@example.com",
            email_type=EmailType.WELCOME,
            context={"name": "John"},
        )

        assert request.to == "test@example.com"
        assert request.email_type == EmailType.WELCOME
        assert request.context == {"name": "John"}

    def test_templated_request_default_context(self):
        """Test templated request with default empty context."""
        request = TemplatedEmailRequest(
            to="test@example.com",
            email_type=EmailType.WELCOME,
        )

        assert request.context == {}

    def test_all_email_types_valid(self):
        """Test all email types are valid."""
        for email_type in EmailType:
            request = TemplatedEmailRequest(
                to="test@example.com",
                email_type=email_type,
            )
            assert request.email_type == email_type


class TestEmailResponse:
    """Tests for EmailResponse schema."""

    def test_success_response(self):
        """Test successful email response."""
        response = EmailResponse(
            success=True,
            message_id="msg-123",
            provider=EmailProvider.RESEND,
        )

        assert response.success is True
        assert response.message_id == "msg-123"
        assert response.provider == EmailProvider.RESEND
        assert response.error is None

    def test_failure_response(self):
        """Test failed email response."""
        response = EmailResponse(
            success=False,
            provider=EmailProvider.RESEND,
            error="API Error: Invalid sender",
        )

        assert response.success is False
        assert response.message_id is None
        assert response.provider == EmailProvider.RESEND
        assert response.error == "API Error: Invalid sender"

    def test_response_with_all_providers(self):
        """Test response with all provider types."""
        for provider in EmailProvider:
            response = EmailResponse(
                success=True,
                message_id="test-id",
                provider=provider,
            )
            assert response.provider == provider


class TestEmailProviderConfig:
    """Tests for EmailProviderConfig schema."""

    def test_valid_config(self):
        """Test valid provider config."""
        config = EmailProviderConfig(
            provider=EmailProvider.RESEND,
            api_key="re_test_key",
            from_email="noreply@example.com",
        )

        assert config.provider == EmailProvider.RESEND
        assert config.api_key == "re_test_key"
        assert config.from_email == "noreply@example.com"
        assert config.from_name is None

    def test_config_with_from_name(self):
        """Test config with from_name."""
        config = EmailProviderConfig(
            provider=EmailProvider.RESEND,
            api_key="re_test",
            from_email="noreply@example.com",
            from_name="My App",
        )

        assert config.from_name == "My App"


class TestEmailEnums:
    """Tests for email enums."""

    def test_email_provider_values(self):
        """Test EmailProvider enum values."""
        assert EmailProvider.RESEND.value == "resend"

    def test_email_type_values(self):
        """Test EmailType enum values."""
        assert EmailType.WELCOME.value == "welcome"
        assert EmailType.PASSWORD_RESET.value == "password_reset"
        assert EmailType.EMAIL_VERIFICATION.value == "email_verification"
        assert EmailType.PAYMENT_SUCCESS.value == "payment_success"
        assert EmailType.PAYMENT_FAILED.value == "payment_failed"
        assert EmailType.GENERIC.value == "generic"

    def test_email_provider_from_string(self):
        """Test creating EmailProvider from string."""
        assert EmailProvider("resend") == EmailProvider.RESEND

    def test_email_type_from_string(self):
        """Test creating EmailType from string."""
        assert EmailType("welcome") == EmailType.WELCOME
        assert EmailType("password_reset") == EmailType.PASSWORD_RESET

    def test_invalid_provider_raises(self):
        """Test invalid provider string raises error."""
        with pytest.raises(ValueError):
            EmailProvider("invalid_provider")

    def test_invalid_type_raises(self):
        """Test invalid email type string raises error."""
        with pytest.raises(ValueError):
            EmailType("invalid_type")
