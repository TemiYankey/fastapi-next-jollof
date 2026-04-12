"""Tests for Paystack payment provider."""

import hashlib
import hmac
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.billing.providers.paystack import PaystackProvider
from app.billing.schemas import CheckoutResponse, PaymentVerificationResponse


class TestPaystackProvider:
    """Tests for Paystack payment provider."""

    @pytest.fixture
    def provider(self):
        """Create Paystack provider instance."""
        with patch("app.billing.providers.paystack.settings") as mock_settings:
            mock_settings.paystack_secret_key = "sk_test_123"
            mock_settings.paystack_public_key = "pk_test_123"
            mock_settings.paystack_webhook_secret = "whsec_test_123"
            return PaystackProvider()

    def test_generate_reference(self, provider):
        """Test reference generation."""
        ref = provider.generate_reference()
        assert ref.startswith("ps_")
        assert len(ref) > 10

    def test_generate_reference_unique(self, provider):
        """Test references are unique."""
        refs = [provider.generate_reference() for _ in range(10)]
        assert len(set(refs)) == 10

    @pytest.mark.asyncio
    async def test_create_checkout_session_success(self, provider):
        """Test successful checkout session creation."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": True,
            "message": "Authorization URL created",
            "data": {
                "authorization_url": "https://checkout.paystack.com/abc123",
                "access_code": "abc123",
                "reference": "ps_test_ref",
            },
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            result = await provider.create_checkout_session(
                amount=Decimal("5000.00"),
                customer_email="test@example.com",
                customer_name="Test User",
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel",
            )

        assert isinstance(result, CheckoutResponse)
        assert result.success is True
        assert result.checkout_url == "https://checkout.paystack.com/abc123"
        assert result.reference is not None
        assert result.metadata["provider"] == "paystack"

    @pytest.mark.asyncio
    async def test_create_checkout_session_with_metadata(self, provider):
        """Test checkout with custom metadata."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": True,
            "data": {
                "authorization_url": "https://checkout.paystack.com/xyz",
                "access_code": "xyz",
                "reference": "ps_meta_ref",
            },
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            result = await provider.create_checkout_session(
                amount=Decimal("1000.00"),
                customer_email="test@example.com",
                customer_name="Test User",
                success_url="https://example.com/success",
                metadata={"plan_name": "Basic Plan"},
            )

        assert result.success is True
        assert result.metadata["access_code"] == "xyz"

    @pytest.mark.asyncio
    async def test_create_checkout_session_api_error(self, provider):
        """Test checkout fails with API error."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "status": False,
            "message": "Invalid email address",
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            result = await provider.create_checkout_session(
                amount=Decimal("1000.00"),
                customer_email="invalid",
                customer_name="Test User",
                success_url="https://example.com/success",
            )

        assert result.success is False
        assert "Invalid email address" in result.error_message

    @pytest.mark.asyncio
    async def test_create_checkout_session_network_error(self, provider):
        """Test checkout handles network error."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.RequestError("Connection failed")
            )

            result = await provider.create_checkout_session(
                amount=Decimal("1000.00"),
                customer_email="test@example.com",
                customer_name="Test User",
                success_url="https://example.com/success",
            )

        assert result.success is False
        assert "Network error" in result.error_message

    @pytest.mark.asyncio
    async def test_verify_payment_success(self, provider):
        """Test successful payment verification."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": True,
            "data": {
                "status": "success",
                "amount": 500000,
                "currency": "NGN",
                "channel": "card",
                "paid_at": "2024-01-15T10:30:00.000Z",
                "customer": {"email": "test@example.com"},
                "id": 123456789,
            },
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await provider.verify_payment("ps_test_ref")

        assert isinstance(result, PaymentVerificationResponse)
        assert result.success is True
        assert result.verified is True
        assert result.amount == Decimal("5000.00")
        assert result.currency == "NGN"

    @pytest.mark.asyncio
    async def test_verify_payment_pending(self, provider):
        """Test payment verification for pending payment."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": True,
            "data": {
                "status": "pending",
                "amount": 100000,
            },
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await provider.verify_payment("ps_pending_ref")

        assert result.success is True
        assert result.verified is False
        assert result.status == "pending"

    @pytest.mark.asyncio
    async def test_verify_payment_failed(self, provider):
        """Test payment verification for failed payment."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": True,
            "data": {
                "status": "failed",
                "amount": 100000,
            },
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await provider.verify_payment("ps_failed_ref")

        assert result.success is True
        assert result.verified is False
        assert result.status == "failed"

    @pytest.mark.asyncio
    async def test_verify_payment_api_error(self, provider):
        """Test verification handles API error."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "status": False,
            "message": "Transaction not found",
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await provider.verify_payment("invalid_ref")

        assert result.success is False
        assert result.verified is False

    @pytest.mark.asyncio
    async def test_verify_payment_network_error(self, provider):
        """Test verification handles network error."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=httpx.RequestError("Connection failed")
            )

            result = await provider.verify_payment("test_ref")

        assert result.success is False
        assert result.verified is False
        assert "Network error" in result.error_message

    @pytest.mark.asyncio
    async def test_handle_webhook_charge_success(self, provider):
        """Test handling charge.success webhook."""
        payload = {
            "event": "charge.success",
            "data": {
                "reference": "ps_webhook_ref",
                "amount": 500000,
                "currency": "NGN",
                "customer": {"email": "webhook@test.com"},
                "id": 987654321,
            },
        }

        result = await provider.handle_webhook(payload)

        assert result["success"] is True
        assert result["event_type"] == "charge.success"
        assert result["reference"] == "ps_webhook_ref"
        assert result["amount"] == 5000.00

    @pytest.mark.asyncio
    async def test_handle_webhook_transfer_success(self, provider):
        """Test handling transfer.success webhook."""
        payload = {
            "event": "transfer.success",
            "data": {
                "reference": "tr_123",
                "amount": 100000,
            },
        }

        result = await provider.handle_webhook(payload)

        assert result["success"] is True
        assert result["event_type"] == "transfer.success"
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_handle_webhook_transfer_failed(self, provider):
        """Test handling transfer.failed webhook."""
        payload = {
            "event": "transfer.failed",
            "data": {
                "reference": "tr_456",
                "reason": "Insufficient balance",
            },
        }

        result = await provider.handle_webhook(payload)

        assert result["success"] is True
        assert result["event_type"] == "transfer.failed"
        assert result["status"] == "failed"
        assert result["reason"] == "Insufficient balance"

    @pytest.mark.asyncio
    async def test_handle_webhook_unknown_event(self, provider):
        """Test handling unknown webhook event."""
        payload = {
            "event": "unknown.event",
            "data": {},
        }

        result = await provider.handle_webhook(payload)

        assert result["success"] is True
        assert result["message"] == "Event received but not processed"

    def test_verify_webhook_signature_valid(self, provider):
        """Test webhook signature verification with valid signature."""
        payload = b'{"event": "charge.success"}'
        expected_hash = hmac.new(
            provider.webhook_secret.encode("utf-8"),
            payload,
            hashlib.sha512,
        ).hexdigest()

        result = provider.verify_webhook_signature(payload, expected_hash)

        assert result is True

    def test_verify_webhook_signature_invalid(self, provider):
        """Test webhook signature verification with invalid signature."""
        payload = b'{"event": "charge.success"}'
        result = provider.verify_webhook_signature(payload, "invalid_signature")

        assert result is False

    def test_verify_webhook_signature_no_secret(self, provider):
        """Test webhook signature verification with no secret configured."""
        provider.webhook_secret = ""
        result = provider.verify_webhook_signature(b"payload", "sig")

        assert result is False

    @pytest.mark.asyncio
    async def test_list_banks_success(self, provider):
        """Test listing banks."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": True,
            "data": [
                {"name": "Access Bank", "code": "044"},
                {"name": "GTBank", "code": "058"},
            ],
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await provider.list_banks()

        assert result["success"] is True
        assert len(result["banks"]) == 2

    @pytest.mark.asyncio
    async def test_list_banks_error(self, provider):
        """Test listing banks handles error."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=Exception("API Error")
            )

            result = await provider.list_banks()

        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_resolve_account_success(self, provider):
        """Test resolving bank account."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": True,
            "data": {
                "account_name": "John Doe",
                "account_number": "0123456789",
            },
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await provider.resolve_account("0123456789", "044")

        assert result["success"] is True
        assert result["account_name"] == "John Doe"

    @pytest.mark.asyncio
    async def test_resolve_account_error(self, provider):
        """Test resolving account handles error."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "status": False,
            "message": "Could not resolve account name",
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await provider.resolve_account("invalid", "000")

        assert result["success"] is False
