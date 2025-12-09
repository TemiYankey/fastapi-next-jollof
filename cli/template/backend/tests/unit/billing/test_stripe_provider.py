"""Tests for Stripe payment provider."""

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import stripe

from app.billing.providers.stripe import StripeProvider
from app.billing.schemas import CheckoutResponse, PaymentVerificationResponse


class TestStripeProvider:
    """Tests for Stripe payment provider."""

    @pytest.fixture
    def provider(self):
        """Create Stripe provider instance."""
        with patch.object(stripe, "api_key", "test_key"):
            return StripeProvider()

    def test_generate_reference(self, provider):
        """Test reference generation."""
        ref = provider.generate_reference()
        assert ref.startswith("stripe_")
        assert len(ref) > 15

    def test_generate_reference_unique(self, provider):
        """Test references are unique."""
        refs = [provider.generate_reference() for _ in range(10)]
        assert len(set(refs)) == 10

    @pytest.mark.asyncio
    async def test_create_checkout_session_success(self, provider):
        """Test successful checkout session creation."""
        mock_session = MagicMock()
        mock_session.id = "cs_test_123"
        mock_session.url = "https://checkout.stripe.com/session123"

        with patch.object(stripe.checkout.Session, "create", return_value=mock_session):
            result = await provider.create_checkout_session(
                amount=Decimal("100.00"),
                customer_email="test@example.com",
                customer_name="Test User",
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel",
            )

        assert isinstance(result, CheckoutResponse)
        assert result.success is True
        assert result.checkout_url == "https://checkout.stripe.com/session123"
        assert result.reference is not None
        assert result.metadata["provider"] == "stripe"

    @pytest.mark.asyncio
    async def test_create_checkout_session_with_metadata(self, provider):
        """Test checkout with custom metadata."""
        mock_session = MagicMock()
        mock_session.id = "cs_test_456"
        mock_session.url = "https://checkout.stripe.com/session456"

        with patch.object(stripe.checkout.Session, "create", return_value=mock_session):
            result = await provider.create_checkout_session(
                amount=Decimal("50.00"),
                customer_email="test@example.com",
                customer_name="Test User",
                success_url="https://example.com/success",
                metadata={"plan_name": "Pro Plan"},
            )

        assert result.success is True
        assert result.metadata["session_id"] == "cs_test_456"

    @pytest.mark.asyncio
    async def test_create_checkout_session_stripe_error(self, provider):
        """Test checkout fails with Stripe error."""
        with patch.object(
            stripe.checkout.Session,
            "create",
            side_effect=stripe.error.StripeError("Card declined"),
        ):
            result = await provider.create_checkout_session(
                amount=Decimal("100.00"),
                customer_email="test@example.com",
                customer_name="Test User",
                success_url="https://example.com/success",
            )

        assert result.success is False
        assert "Card declined" in result.error_message

    @pytest.mark.asyncio
    async def test_create_checkout_session_unexpected_error(self, provider):
        """Test checkout handles unexpected error."""
        with patch.object(
            stripe.checkout.Session,
            "create",
            side_effect=Exception("Network error"),
        ):
            result = await provider.create_checkout_session(
                amount=Decimal("100.00"),
                customer_email="test@example.com",
                customer_name="Test User",
                success_url="https://example.com/success",
            )

        assert result.success is False
        assert result.error_message == "Failed to create checkout session"

    @pytest.mark.asyncio
    async def test_verify_payment_success(self, provider):
        """Test successful payment verification."""
        mock_session = MagicMock()
        mock_session.payment_status = "paid"
        mock_session.amount_total = 10000
        mock_session.currency = "usd"
        mock_session.customer_email = "test@example.com"
        mock_session.id = "cs_test_789"
        mock_session.payment_intent = "pi_test_123"
        mock_session.metadata = {"order_reference": "stripe_test_ref"}

        mock_payment_intent = MagicMock()
        mock_payment_intent.payment_method_types = ["card"]

        mock_sessions = MagicMock()
        mock_sessions.auto_paging_iter.return_value = [mock_session]

        with (
            patch.object(stripe.checkout.Session, "list", return_value=mock_sessions),
            patch.object(stripe.PaymentIntent, "retrieve", return_value=mock_payment_intent),
        ):
            result = await provider.verify_payment("stripe_test_ref")

        assert isinstance(result, PaymentVerificationResponse)
        assert result.success is True
        assert result.verified is True
        assert result.amount == Decimal("100.00")
        assert result.currency == "USD"

    @pytest.mark.asyncio
    async def test_verify_payment_pending(self, provider):
        """Test payment verification for pending payment."""
        mock_session = MagicMock()
        mock_session.payment_status = "unpaid"
        mock_session.metadata = {"order_reference": "stripe_pending_ref"}

        mock_sessions = MagicMock()
        mock_sessions.auto_paging_iter.return_value = [mock_session]

        with patch.object(stripe.checkout.Session, "list", return_value=mock_sessions):
            result = await provider.verify_payment("stripe_pending_ref")

        assert result.success is True
        assert result.verified is False
        assert result.status == "unpaid"

    @pytest.mark.asyncio
    async def test_verify_payment_not_found(self, provider):
        """Test verification when session not found."""
        mock_sessions = MagicMock()
        mock_sessions.auto_paging_iter.return_value = []

        with patch.object(stripe.checkout.Session, "list", return_value=mock_sessions):
            result = await provider.verify_payment("nonexistent_ref")

        assert result.success is False
        assert result.verified is False
        assert "No session found" in result.error_message

    @pytest.mark.asyncio
    async def test_verify_payment_stripe_error(self, provider):
        """Test verification handles Stripe error."""
        with patch.object(
            stripe.checkout.Session,
            "list",
            side_effect=stripe.error.StripeError("API error"),
        ):
            result = await provider.verify_payment("test_ref")

        assert result.success is False
        assert result.verified is False

    @pytest.mark.asyncio
    async def test_handle_webhook_checkout_completed(self, provider):
        """Test handling checkout.session.completed webhook."""
        mock_event = MagicMock()
        mock_event.type = "checkout.session.completed"
        mock_event.data.object.id = "cs_test_webhook"
        mock_event.data.object.payment_status = "paid"
        mock_event.data.object.amount_total = 5000
        mock_event.data.object.customer_email = "webhook@test.com"
        mock_event.data.object.metadata = {"order_reference": "webhook_ref"}

        with patch.object(stripe.Event, "construct_from", return_value=mock_event):
            result = await provider.handle_webhook({"type": "checkout.session.completed"})

        assert result["success"] is True
        assert result["event_type"] == "checkout.session.completed"
        assert result["reference"] == "webhook_ref"

    @pytest.mark.asyncio
    async def test_handle_webhook_payment_succeeded(self, provider):
        """Test handling payment_intent.succeeded webhook."""
        mock_event = MagicMock()
        mock_event.type = "payment_intent.succeeded"
        mock_event.data.object.id = "pi_test_123"
        mock_event.data.object.amount = 10000
        mock_event.data.object.status = "succeeded"

        with patch.object(stripe.Event, "construct_from", return_value=mock_event):
            result = await provider.handle_webhook({"type": "payment_intent.succeeded"})

        assert result["success"] is True
        assert result["event_type"] == "payment_intent.succeeded"

    @pytest.mark.asyncio
    async def test_handle_webhook_payment_failed(self, provider):
        """Test handling payment_intent.payment_failed webhook."""
        mock_event = MagicMock()
        mock_event.type = "payment_intent.payment_failed"
        mock_event.data.object.id = "pi_failed_123"
        mock_event.data.object.last_payment_error = MagicMock()
        mock_event.data.object.last_payment_error.message = "Card declined"

        with patch.object(stripe.Event, "construct_from", return_value=mock_event):
            result = await provider.handle_webhook({"type": "payment_intent.payment_failed"})

        assert result["success"] is True
        assert result["event_type"] == "payment_intent.payment_failed"
        assert result["error"] == "Card declined"

    @pytest.mark.asyncio
    async def test_handle_webhook_unknown_event(self, provider):
        """Test handling unknown webhook event."""
        mock_event = MagicMock()
        mock_event.type = "unknown.event"
        mock_event.data.object = {}

        with patch.object(stripe.Event, "construct_from", return_value=mock_event):
            result = await provider.handle_webhook({"type": "unknown.event"})

        assert result["success"] is True
        assert result["message"] == "Event received but not processed"

    def test_verify_webhook_signature_valid(self, provider):
        """Test webhook signature verification with valid signature."""
        with patch.object(stripe.Webhook, "construct_event", return_value=MagicMock()):
            result = provider.verify_webhook_signature(b"payload", "valid_sig")

        assert result is True

    def test_verify_webhook_signature_invalid(self, provider):
        """Test webhook signature verification with invalid signature."""
        with patch.object(
            stripe.Webhook,
            "construct_event",
            side_effect=stripe.error.SignatureVerificationError("Invalid", "sig"),
        ):
            result = provider.verify_webhook_signature(b"payload", "invalid_sig")

        assert result is False
