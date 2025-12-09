"""Tests for Nomba payment provider."""

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.billing.providers.nomba import (
    NombaAPIException,
    NombaPaymentProvider,
)


class TestNombaAPIException:
    """Tests for NombaAPIException."""

    def test_exception_with_message(self):
        """Test exception with message only."""
        exc = NombaAPIException("Test error")

        assert str(exc) == "Test error"
        assert exc.message == "Test error"
        assert exc.status_code is None
        assert exc.response_data is None

    def test_exception_with_status_code(self):
        """Test exception with status code."""
        exc = NombaAPIException("Test error", status_code=400)

        assert exc.message == "Test error"
        assert exc.status_code == 400

    def test_exception_with_response_data(self):
        """Test exception with response data."""
        response_data = {"error": "invalid_request"}
        exc = NombaAPIException("Test error", response_data=response_data)

        assert exc.response_data == response_data

    def test_exception_with_all_params(self):
        """Test exception with all parameters."""
        response_data = {"code": "ERR001"}
        exc = NombaAPIException("Full error", status_code=500, response_data=response_data)

        assert exc.message == "Full error"
        assert exc.status_code == 500
        assert exc.response_data == response_data


class TestNombaPaymentProviderInit:
    """Tests for NombaPaymentProvider initialization."""

    def test_provider_initialization(self):
        """Test provider initializes with settings."""
        with patch("app.billing.providers.nomba.settings") as mock_settings:
            mock_settings.nomba_client_id = "client-123"
            mock_settings.nomba_client_secret = "secret-456"
            mock_settings.nomba_account_id = "account-789"

            provider = NombaPaymentProvider()

            assert provider._client_id == "client-123"
            assert provider._client_secret == "secret-456"
            assert provider._account_id == "account-789"
            assert provider._access_token is None
            assert provider._token_expires_at is None

    def test_base_url(self):
        """Test provider has correct base URL."""
        assert NombaPaymentProvider.BASE_URL == "https://api.nomba.com/v1"


class TestGenerateReference:
    """Tests for generate_reference method."""

    def test_generates_unique_reference(self):
        """Test generates unique references."""
        with patch("app.billing.providers.nomba.settings"):
            provider = NombaPaymentProvider()

            ref1 = provider.generate_reference()
            ref2 = provider.generate_reference()

            assert ref1 != ref2

    def test_reference_format(self):
        """Test reference follows expected format."""
        with patch("app.billing.providers.nomba.settings"):
            provider = NombaPaymentProvider()

            ref = provider.generate_reference()

            assert ref.startswith("PAY-")
            parts = ref.split("-")
            assert len(parts) == 3
            # Second part is timestamp (14 chars)
            assert len(parts[1]) == 14
            # Third part is unique ID (8 chars)
            assert len(parts[2]) == 8


class TestGetAccessToken:
    """Tests for _get_access_token method."""

    @pytest.mark.asyncio
    async def test_returns_cached_token(self):
        """Test returns cached token when valid."""
        with patch("app.billing.providers.nomba.settings"):
            with patch("app.billing.providers.nomba.utcnow") as mock_utcnow:
                from datetime import datetime, timedelta

                now = datetime(2024, 1, 1, 12, 0, 0)
                mock_utcnow.return_value = now

                provider = NombaPaymentProvider()
                provider._access_token = "cached-token"
                provider._token_expires_at = now + timedelta(hours=1)

                token = await provider._get_access_token()

                assert token == "cached-token"

    @pytest.mark.asyncio
    async def test_fetches_new_token_when_expired(self):
        """Test fetches new token when cached is expired."""
        with patch("app.billing.providers.nomba.settings") as mock_settings:
            mock_settings.nomba_client_id = "client-123"
            mock_settings.nomba_client_secret = "secret-456"
            mock_settings.nomba_account_id = "account-789"

            with patch("app.billing.providers.nomba.utcnow") as mock_utcnow:
                from datetime import datetime, timedelta

                now = datetime(2024, 1, 1, 12, 0, 0)
                mock_utcnow.return_value = now

                provider = NombaPaymentProvider()
                provider._access_token = "expired-token"
                provider._token_expires_at = now - timedelta(hours=1)  # Expired

                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "data": {"access_token": "new-token"},
                    "expires_in": 3600,
                }

                with patch("httpx.AsyncClient") as mock_client:
                    mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                        return_value=mock_response
                    )

                    token = await provider._get_access_token()

                    assert token == "new-token"
                    assert provider._access_token == "new-token"

    @pytest.mark.asyncio
    async def test_raises_on_token_request_failure(self):
        """Test raises exception on token request failure."""
        with patch("app.billing.providers.nomba.settings") as mock_settings:
            mock_settings.nomba_client_id = "client-123"
            mock_settings.nomba_client_secret = "secret-456"
            mock_settings.nomba_account_id = "account-789"

            provider = NombaPaymentProvider()

            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.json.return_value = {"error": "invalid_credentials"}
            mock_response.content = b'{"error": "invalid_credentials"}'

            with patch("httpx.AsyncClient") as mock_client:
                mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                    return_value=mock_response
                )

                with pytest.raises(NombaAPIException) as exc:
                    await provider._get_access_token()

                assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_raises_on_network_error(self):
        """Test raises exception on network error."""
        with patch("app.billing.providers.nomba.settings") as mock_settings:
            mock_settings.nomba_client_id = "client-123"
            mock_settings.nomba_client_secret = "secret-456"
            mock_settings.nomba_account_id = "account-789"

            provider = NombaPaymentProvider()

            with patch("httpx.AsyncClient") as mock_client:
                mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                    side_effect=httpx.RequestError("Connection refused")
                )

                with pytest.raises(NombaAPIException) as exc:
                    await provider._get_access_token()

                assert "Network error" in exc.value.message


class TestCreateCheckoutSession:
    """Tests for create_checkout_session method."""

    @pytest.mark.asyncio
    async def test_successful_checkout_session(self):
        """Test successful checkout session creation."""
        with patch("app.billing.providers.nomba.settings") as mock_settings:
            mock_settings.nomba_client_id = "client-123"
            mock_settings.nomba_client_secret = "secret-456"
            mock_settings.nomba_account_id = "account-789"

            provider = NombaPaymentProvider()

            with patch.object(
                provider, "_make_authenticated_request", new_callable=AsyncMock
            ) as mock_request:
                mock_request.return_value = {
                    "data": {"checkoutLink": "https://checkout.nomba.com/pay/123"},
                    "status": "success",
                    "description": "Order created",
                }

                result = await provider.create_checkout_session(
                    amount=Decimal("10.00"),
                    customer_email="test@example.com",
                    customer_name="Test User",
                    success_url="https://example.com/success",
                    order_reference="REF-123",
                )

                assert result.success is True
                assert result.checkout_url == "https://checkout.nomba.com/pay/123"
                assert result.reference == "REF-123"

    @pytest.mark.asyncio
    async def test_checkout_session_api_error(self):
        """Test checkout session handles API error."""
        with patch("app.billing.providers.nomba.settings") as mock_settings:
            mock_settings.nomba_client_id = "client-123"
            mock_settings.nomba_client_secret = "secret-456"
            mock_settings.nomba_account_id = "account-789"

            provider = NombaPaymentProvider()

            with patch.object(
                provider, "_make_authenticated_request", new_callable=AsyncMock
            ) as mock_request:
                mock_request.side_effect = NombaAPIException(
                    "Invalid amount", status_code=400
                )

                result = await provider.create_checkout_session(
                    amount=Decimal("-10.00"),
                    customer_email="test@example.com",
                    customer_name="Test User",
                    success_url="https://example.com/success",
                )

                assert result.success is False
                assert "Invalid amount" in result.error_message

    @pytest.mark.asyncio
    async def test_checkout_session_generates_reference(self):
        """Test checkout session generates reference if not provided."""
        with patch("app.billing.providers.nomba.settings") as mock_settings:
            mock_settings.nomba_client_id = "client-123"
            mock_settings.nomba_client_secret = "secret-456"
            mock_settings.nomba_account_id = "account-789"

            provider = NombaPaymentProvider()

            with patch.object(
                provider, "_make_authenticated_request", new_callable=AsyncMock
            ) as mock_request:
                mock_request.return_value = {
                    "data": {"checkoutLink": "https://checkout.nomba.com/pay/123"},
                    "status": "success",
                }

                result = await provider.create_checkout_session(
                    amount=Decimal("10.00"),
                    customer_email="test@example.com",
                    customer_name="Test User",
                    success_url="https://example.com/success",
                    # No order_reference provided
                )

                assert result.success is True
                assert result.reference.startswith("PAY-")


class TestVerifyPayment:
    """Tests for verify_payment method."""

    @pytest.mark.asyncio
    async def test_successful_verification(self):
        """Test successful payment verification."""
        with patch("app.billing.providers.nomba.settings") as mock_settings:
            mock_settings.nomba_client_id = "client-123"
            mock_settings.nomba_client_secret = "secret-456"
            mock_settings.nomba_account_id = "account-789"

            provider = NombaPaymentProvider()

            with patch.object(
                provider, "_make_authenticated_request", new_callable=AsyncMock
            ) as mock_request:
                mock_request.return_value = {
                    "data": {
                        "success": True,
                        "order": {
                            "amount": "1000.00",
                            "currency": "NGN",
                            "customerEmail": "test@example.com",
                        },
                        "transactionDetails": {
                            "transactionDate": "2024-01-01T12:00:00Z",
                            "paymentReference": "PAY-REF-123",
                        },
                        "cardDetails": {"last4": "1234"},
                    }
                }

                result = await provider.verify_payment("REF-123")

                assert result.success is True
                assert result.verified is True
                assert result.status == "success"
                assert result.payment_method == "card"

    @pytest.mark.asyncio
    async def test_verification_not_found(self):
        """Test verification when payment not found."""
        with patch("app.billing.providers.nomba.settings") as mock_settings:
            mock_settings.nomba_client_id = "client-123"
            mock_settings.nomba_client_secret = "secret-456"
            mock_settings.nomba_account_id = "account-789"

            provider = NombaPaymentProvider()

            with patch.object(
                provider, "_make_authenticated_request", new_callable=AsyncMock
            ) as mock_request:
                mock_request.side_effect = NombaAPIException(
                    "Transaction not found", status_code=404
                )

                result = await provider.verify_payment("INVALID-REF")

                assert result.success is False
                assert result.verified is False
                assert "not found" in result.error_message.lower()

    @pytest.mark.asyncio
    async def test_verification_with_bank_transfer(self):
        """Test verification detects bank transfer method."""
        with patch("app.billing.providers.nomba.settings") as mock_settings:
            mock_settings.nomba_client_id = "client-123"
            mock_settings.nomba_client_secret = "secret-456"
            mock_settings.nomba_account_id = "account-789"

            provider = NombaPaymentProvider()

            with patch.object(
                provider, "_make_authenticated_request", new_callable=AsyncMock
            ) as mock_request:
                mock_request.return_value = {
                    "data": {
                        "success": True,
                        "order": {
                            "amount": "1000.00",
                            "currency": "NGN",
                        },
                        "transactionDetails": {},
                        "transferDetails": {"bankName": "Test Bank"},
                    }
                }

                result = await provider.verify_payment("REF-123")

                assert result.payment_method == "bank_transfer"


class TestHandleWebhook:
    """Tests for handle_webhook method."""

    @pytest.mark.asyncio
    async def test_successful_webhook_handling(self):
        """Test successful webhook handling."""
        with patch("app.billing.providers.nomba.settings"):
            provider = NombaPaymentProvider()

            payload = {
                "orderReference": "ORD-123",
                "paymentReference": "PAY-456",
                "status": "success",
                "amount": "1000.00",
                "customerEmail": "test@example.com",
            }

            result = await provider.handle_webhook(payload)

            assert result["success"] is True
            assert result["processed"] is True
            assert result["order_reference"] == "ORD-123"
            assert result["status"] == "success"
            assert result["amount"] == Decimal("1000.00")

    @pytest.mark.asyncio
    async def test_webhook_handling_failed_status(self):
        """Test webhook handling with failed status."""
        with patch("app.billing.providers.nomba.settings"):
            provider = NombaPaymentProvider()

            payload = {
                "orderReference": "ORD-123",
                "status": "failed",
                "amount": "0",
            }

            result = await provider.handle_webhook(payload)

            assert result["success"] is True
            assert result["status"] == "failed"

    @pytest.mark.asyncio
    async def test_webhook_handling_exception(self):
        """Test webhook handling with exception."""
        with patch("app.billing.providers.nomba.settings"):
            provider = NombaPaymentProvider()

            # Invalid payload that causes parsing error
            payload = {"amount": "not-a-number"}

            result = await provider.handle_webhook(payload)

            assert result["success"] is False
            assert result["processed"] is False
            assert "error" in result


class TestMapStatus:
    """Tests for _map_status method."""

    def test_maps_success_statuses(self):
        """Test maps success-related statuses."""
        with patch("app.billing.providers.nomba.settings"):
            provider = NombaPaymentProvider()

            assert provider._map_status("success") == "success"
            assert provider._map_status("successful") == "success"
            assert provider._map_status("completed") == "success"
            assert provider._map_status("SUCCESS") == "success"

    def test_maps_failed_statuses(self):
        """Test maps failed-related statuses."""
        with patch("app.billing.providers.nomba.settings"):
            provider = NombaPaymentProvider()

            assert provider._map_status("failed") == "failed"
            assert provider._map_status("failure") == "failed"
            assert provider._map_status("FAILED") == "failed"

    def test_maps_cancelled_statuses(self):
        """Test maps cancelled-related statuses."""
        with patch("app.billing.providers.nomba.settings"):
            provider = NombaPaymentProvider()

            assert provider._map_status("cancelled") == "cancelled"
            assert provider._map_status("canceled") == "cancelled"

    def test_maps_pending_statuses(self):
        """Test maps pending-related statuses."""
        with patch("app.billing.providers.nomba.settings"):
            provider = NombaPaymentProvider()

            assert provider._map_status("pending") == "pending"
            assert provider._map_status("processing") == "pending"

    def test_unknown_status_defaults_to_pending(self):
        """Test unknown status defaults to pending."""
        with patch("app.billing.providers.nomba.settings"):
            provider = NombaPaymentProvider()

            assert provider._map_status("unknown") == "pending"
            assert provider._map_status("random") == "pending"


class TestMakeAuthenticatedRequest:
    """Tests for _make_authenticated_request method."""

    @pytest.mark.asyncio
    async def test_handles_400_error(self):
        """Test handles 400 Bad Request error."""
        with patch("app.billing.providers.nomba.settings") as mock_settings:
            mock_settings.nomba_client_id = "client-123"
            mock_settings.nomba_client_secret = "secret-456"
            mock_settings.nomba_account_id = "account-789"

            provider = NombaPaymentProvider()

            with patch.object(
                provider, "_get_access_token", new_callable=AsyncMock
            ) as mock_token:
                mock_token.return_value = "test-token"

                mock_response = MagicMock()
                mock_response.status_code = 400
                mock_response.json.return_value = {"message": "Bad request"}

                with patch("httpx.AsyncClient") as mock_client:
                    mock_client.return_value.__aenter__.return_value.request = AsyncMock(
                        return_value=mock_response
                    )

                    with pytest.raises(NombaAPIException) as exc:
                        await provider._make_authenticated_request("POST", "/test")

                    assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_handles_401_error(self):
        """Test handles 401 Unauthorized error."""
        with patch("app.billing.providers.nomba.settings") as mock_settings:
            mock_settings.nomba_client_id = "client-123"
            mock_settings.nomba_client_secret = "secret-456"
            mock_settings.nomba_account_id = "account-789"

            provider = NombaPaymentProvider()

            with patch.object(
                provider, "_get_access_token", new_callable=AsyncMock
            ) as mock_token:
                mock_token.return_value = "test-token"

                mock_response = MagicMock()
                mock_response.status_code = 401
                mock_response.json.return_value = {"message": "Unauthorized"}

                with patch("httpx.AsyncClient") as mock_client:
                    mock_client.return_value.__aenter__.return_value.request = AsyncMock(
                        return_value=mock_response
                    )

                    with pytest.raises(NombaAPIException) as exc:
                        await provider._make_authenticated_request("GET", "/test")

                    assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_handles_nomba_error_code(self):
        """Test handles non-00 Nomba error code."""
        with patch("app.billing.providers.nomba.settings") as mock_settings:
            mock_settings.nomba_client_id = "client-123"
            mock_settings.nomba_client_secret = "secret-456"
            mock_settings.nomba_account_id = "account-789"

            provider = NombaPaymentProvider()

            with patch.object(
                provider, "_get_access_token", new_callable=AsyncMock
            ) as mock_token:
                mock_token.return_value = "test-token"

                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "code": "ERR01",
                    "description": "Custom error",
                }

                with patch("httpx.AsyncClient") as mock_client:
                    mock_client.return_value.__aenter__.return_value.request = AsyncMock(
                        return_value=mock_response
                    )

                    with pytest.raises(NombaAPIException) as exc:
                        await provider._make_authenticated_request("GET", "/test")

                    assert "Custom error" in exc.value.message
