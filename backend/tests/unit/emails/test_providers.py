"""Tests for email providers (Resend and Brevo)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.emails.enums import EmailProvider
from app.emails.providers.brevo import BrevoProvider
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
    async def test_send_with_custom_from(self):
        """Test email send with custom from address."""
        request = EmailRequestFactory.create_with_custom_from()

        with SettingsFactory.mock():
            with patch("app.emails.providers.resend.resend") as mock_resend:
                with patch("app.emails.providers.resend.asyncio.to_thread") as mock_to_thread:
                    mock_to_thread.return_value = {"id": "test-id"}

                    response = await ResendProvider.send(request)

                    call_args = mock_to_thread.call_args
                    params = call_args[0][1]
                    assert "Custom Sender <custom@example.com>" in params["from"]

    @pytest.mark.asyncio
    async def test_send_with_reply_to(self):
        """Test email send with reply-to address."""
        request = EmailRequestFactory.create_with_reply_to()

        with SettingsFactory.mock():
            with patch("app.emails.providers.resend.resend") as mock_resend:
                with patch("app.emails.providers.resend.asyncio.to_thread") as mock_to_thread:
                    mock_to_thread.return_value = {"id": "test-id"}

                    await ResendProvider.send(request)

                    call_args = mock_to_thread.call_args
                    params = call_args[0][1]
                    assert params.get("reply_to") == "reply@example.com"

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
    async def test_send_resend_error(self):
        """Test handling of Resend SDK error."""
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
                    assert "Resend Error" in response.error

    @pytest.mark.asyncio
    async def test_send_generic_error(self):
        """Test handling of generic exception."""
        email_request = EmailRequestFactory.create()

        with SettingsFactory.mock():
            with patch("app.emails.providers.resend.resend") as mock_resend:
                with patch("app.emails.providers.resend.asyncio.to_thread") as mock_to_thread:
                    mock_resend.exceptions.ResendError = Exception
                    mock_to_thread.side_effect = ValueError("Unexpected error")

                    response = await ResendProvider.send(email_request)

                    assert response.success is False
                    assert "Unexpected error" in response.error

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

    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """Test health check failure."""
        with SettingsFactory.mock():
            with patch("app.emails.providers.resend.resend") as mock_resend:
                with patch("app.emails.providers.resend.asyncio.to_thread") as mock_to_thread:
                    mock_to_thread.side_effect = Exception("Connection failed")

                    result = await ResendProvider.health_check()

                    assert result is False


class TestBrevoProvider:
    """Tests for BrevoProvider."""

    @pytest.mark.asyncio
    async def test_send_success(self):
        """Test successful email send via Brevo."""
        email_request = EmailRequestFactory.create(text_content=None)

        with SettingsFactory.mock():
            with patch("app.emails.providers.brevo.httpx.AsyncClient") as mock_client:
                mock_response = MagicMock()
                mock_response.status_code = 201
                mock_response.json.return_value = {"messageId": "brevo-message-id-123"}

                mock_instance = AsyncMock()
                mock_instance.post.return_value = mock_response
                mock_client.return_value.__aenter__.return_value = mock_instance

                response = await BrevoProvider.send(email_request)

                assert response.success is True
                assert response.message_id == "brevo-message-id-123"
                assert response.provider == EmailProvider.BREVO
                assert response.error is None

    @pytest.mark.asyncio
    async def test_send_verifies_payload_structure(self):
        """Test that Brevo payload has correct structure (Writera-tested format)."""
        email_request = EmailRequestFactory.create(text_content=None)

        with SettingsFactory.mock():
            with patch("app.emails.providers.brevo.httpx.AsyncClient") as mock_client:
                mock_response = MagicMock()
                mock_response.status_code = 201
                mock_response.json.return_value = {"messageId": "test-id"}

                mock_instance = AsyncMock()
                mock_instance.post.return_value = mock_response
                mock_client.return_value.__aenter__.return_value = mock_instance

                await BrevoProvider.send(email_request)

                call_args = mock_instance.post.call_args
                url = call_args[0][0]
                payload = call_args[1]["json"]
                headers = call_args[1]["headers"]

                # Verify URL
                assert url == "https://api.brevo.com/v3/smtp/email"

                # Verify payload structure (exact Writera format)
                assert "sender" in payload
                assert "name" in payload["sender"]
                assert "email" in payload["sender"]
                assert "to" in payload
                assert isinstance(payload["to"], list)
                assert "email" in payload["to"][0]
                assert "subject" in payload
                assert "htmlContent" in payload

                # Verify headers
                assert headers["api-key"] == "xkeysib_test_key"
                assert headers["content-type"] == "application/json"
                assert headers["accept"] == "application/json"

    @pytest.mark.asyncio
    async def test_send_with_attachment(self):
        """Test email send with base64-encoded attachment."""
        email_request = EmailRequestFactory.create(text_content=None)
        attachment_content = b"PDF content here"
        attachment_filename = "document.pdf"

        with SettingsFactory.mock():
            with patch("app.emails.providers.brevo.httpx.AsyncClient") as mock_client:
                mock_response = MagicMock()
                mock_response.status_code = 201
                mock_response.json.return_value = {"messageId": "test-id"}

                mock_instance = AsyncMock()
                mock_instance.post.return_value = mock_response
                mock_client.return_value.__aenter__.return_value = mock_instance

                await BrevoProvider.send(
                    email_request,
                    attachment_content=attachment_content,
                    attachment_filename=attachment_filename,
                )

                call_args = mock_instance.post.call_args
                payload = call_args[1]["json"]

                assert "attachment" in payload
                assert len(payload["attachment"]) == 1
                assert payload["attachment"][0]["name"] == "document.pdf"
                assert "content" in payload["attachment"][0]

    @pytest.mark.asyncio
    async def test_send_api_error(self):
        """Test handling of Brevo API error response."""
        email_request = EmailRequestFactory.create(text_content=None)

        with SettingsFactory.mock():
            with patch("app.emails.providers.brevo.httpx.AsyncClient") as mock_client:
                mock_response = MagicMock()
                mock_response.status_code = 400
                mock_response.text = "Bad Request: Invalid email"

                mock_instance = AsyncMock()
                mock_instance.post.return_value = mock_response
                mock_client.return_value.__aenter__.return_value = mock_instance

                response = await BrevoProvider.send(email_request)

                assert response.success is False
                assert response.provider == EmailProvider.BREVO
                assert "400" in response.error
                assert "Bad Request" in response.error

    @pytest.mark.asyncio
    async def test_send_timeout(self):
        """Test handling of request timeout."""
        import httpx

        email_request = EmailRequestFactory.create(text_content=None)

        with SettingsFactory.mock():
            with patch("app.emails.providers.brevo.httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_instance.post.side_effect = httpx.TimeoutException("Timeout")
                mock_client.return_value.__aenter__.return_value = mock_instance

                response = await BrevoProvider.send(email_request)

                assert response.success is False
                assert response.error == "Request timeout"

    @pytest.mark.asyncio
    async def test_send_generic_exception(self):
        """Test handling of generic exception."""
        email_request = EmailRequestFactory.create(text_content=None)

        with SettingsFactory.mock():
            with patch("app.emails.providers.brevo.httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_instance.post.side_effect = Exception("Network error")
                mock_client.return_value.__aenter__.return_value = mock_instance

                response = await BrevoProvider.send(email_request)

                assert response.success is False
                assert "Brevo Error" in response.error

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test successful health check."""
        with SettingsFactory.mock():
            with patch("app.emails.providers.brevo.httpx.AsyncClient") as mock_client:
                mock_response = MagicMock()
                mock_response.status_code = 200

                mock_instance = AsyncMock()
                mock_instance.get.return_value = mock_response
                mock_client.return_value.__aenter__.return_value = mock_instance

                result = await BrevoProvider.health_check()

                assert result is True

                call_args = mock_instance.get.call_args
                assert "https://api.brevo.com/v3/account" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_health_check_no_api_key(self):
        """Test health check with no API key."""
        with SettingsFactory.mock(brevo_api_key=""):
            result = await BrevoProvider.health_check()
            assert result is False

    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """Test health check failure."""
        with SettingsFactory.mock():
            with patch("app.emails.providers.brevo.httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_instance.get.side_effect = Exception("Connection failed")
                mock_client.return_value.__aenter__.return_value = mock_instance

                result = await BrevoProvider.health_check()

                assert result is False
