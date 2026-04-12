"""Tests for email provider."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.emails.enums import EmailProvider
from app.emails.providers.resend import ResendProvider

from .factories import EmailRequestFactory, SettingsFactory


class TestResendProvider:
    """Tests for ResendProvider."""

    @pytest.mark.asyncio
    async def test_send_success(self):
        """Test successful email send via Resend."""
        email_request = EmailRequestFactory.create()

        with SettingsFactory.mock():
            with patch("app.emails.providers.resend.resend") as mock_resend:
                with patch("app.emails.providers.resend.asyncio.to_thread") as mock_to_thread:
                    mock_to_thread.return_value = {"id": "resend-message-id-123"}

                    response = await ResendProvider.send(email_request)

                    assert response.success is True
                    assert response.message_id == "resend-message-id-123"
                    assert response.provider == EmailProvider.RESEND
                    assert response.error is None

    @pytest.mark.asyncio
    async def test_send_with_attachment(self):
        """Test email send with attachment."""
        email_request = EmailRequestFactory.create()
        attachment_content = b"PDF content here"
        attachment_filename = "document.pdf"

        with SettingsFactory.mock():
            with patch("app.emails.providers.resend.resend") as mock_resend:
                with patch("app.emails.providers.resend.asyncio.to_thread") as mock_to_thread:
                    mock_to_thread.return_value = {"id": "test-id"}

                    await ResendProvider.send(
                        email_request,
                        attachment_content=attachment_content,
                        attachment_filename=attachment_filename,
                    )

                    call_args = mock_to_thread.call_args
                    params = call_args[0][1]
                    assert "attachments" in params
                    assert params["attachments"][0]["filename"] == "document.pdf"

    @pytest.mark.asyncio
    async def test_send_error(self):
        """Test handling of Resend error."""
        email_request = EmailRequestFactory.create()

        with SettingsFactory.mock():
            with patch("app.emails.providers.resend.resend") as mock_resend:
                with patch("app.emails.providers.resend.asyncio.to_thread") as mock_to_thread:
                    class MockResendError(Exception):
                        pass

                    mock_resend.exceptions.ResendError = MockResendError
                    mock_to_thread.side_effect = MockResendError("API Error")

                    response = await ResendProvider.send(email_request)

                    assert response.success is False
                    assert response.provider == EmailProvider.RESEND

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test successful health check."""
        with SettingsFactory.mock():
            with patch("app.emails.providers.resend.resend") as mock_resend:
                with patch("app.emails.providers.resend.asyncio.to_thread") as mock_to_thread:
                    mock_to_thread.return_value = []

                    result = await ResendProvider.health_check()

                    assert result is True

    @pytest.mark.asyncio
    async def test_health_check_no_api_key(self):
        """Test health check with no API key."""
        with SettingsFactory.mock(resend_api_key=""):
            result = await ResendProvider.health_check()
            assert result is False
