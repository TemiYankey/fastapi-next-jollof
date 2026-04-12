"""Tests for payment schemas."""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.billing.schemas import (
    CheckoutRequest,
    CheckoutResponse,
    CreditsOverviewResponse,
    PaymentHistoryResponse,
    PaymentVerificationResponse,
    PlanResponse,
)


class TestCheckoutRequest:
    """Tests for CheckoutRequest schema."""

    def test_valid_checkout_request(self):
        """Test valid checkout request."""
        request = CheckoutRequest(
            plan_id="pkg-123",
            plan_name="Basic Package",
            amount=Decimal("10.00"),
            credits=100,
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
        )

        assert request.plan_id == "pkg-123"
        assert request.amount == Decimal("10.00")
        assert request.credits == 100

    def test_amount_must_be_positive(self):
        """Test that amount must be positive."""
        with pytest.raises(ValidationError) as exc:
            CheckoutRequest(
                plan_id="pkg-123",
                plan_name="Basic Package",
                amount=Decimal("0"),
                credits=100,
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel",
            )

        assert "amount" in str(exc.value).lower()

    def test_amount_negative_fails(self):
        """Test that negative amount fails."""
        with pytest.raises(ValidationError):
            CheckoutRequest(
                plan_id="pkg-123",
                plan_name="Basic Package",
                amount=Decimal("-10.00"),
                credits=100,
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel",
            )

    def test_credits_can_be_zero(self):
        """Test that credits can be zero (for subscriptions without credits)."""
        checkout = CheckoutRequest(
            plan_id="sub-monthly",
            plan_name="Pro Monthly",
            amount=Decimal("10.00"),
            credits=0,
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
        )

        assert checkout.credits == 0

    def test_credits_negative_fails(self):
        """Test that negative credits fails."""
        with pytest.raises(ValidationError):
            CheckoutRequest(
                plan_id="pkg-123",
                plan_name="Basic Package",
                amount=Decimal("10.00"),
                credits=-100,
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel",
            )

    def test_missing_required_fields(self):
        """Test that missing required fields raises error."""
        with pytest.raises(ValidationError):
            CheckoutRequest(
                plan_id="pkg-123",
                # Missing other required fields
            )


class TestCheckoutResponse:
    """Tests for CheckoutResponse schema."""

    def test_successful_checkout_response(self):
        """Test successful checkout response."""
        response = CheckoutResponse(
            success=True,
            checkout_url="https://payment.example.com/checkout/123",
            reference="REF-123",
        )

        assert response.success is True
        assert response.checkout_url is not None
        assert response.error_message is None

    def test_failed_checkout_response(self):
        """Test failed checkout response."""
        response = CheckoutResponse(
            success=False,
            error_message="Payment provider unavailable",
        )

        assert response.success is False
        assert response.checkout_url is None
        assert response.error_message == "Payment provider unavailable"

    def test_metadata_default(self):
        """Test metadata defaults to empty dict."""
        response = CheckoutResponse(success=True)

        assert response.metadata == {}


class TestPaymentVerificationResponse:
    """Tests for PaymentVerificationResponse schema."""

    def test_verified_payment(self):
        """Test verified payment response."""
        response = PaymentVerificationResponse(
            success=True,
            verified=True,
            status="success",
            amount=Decimal("10.00"),
            currency="NGN",
            payment_method="card",
            paid_at=datetime.now(),
            customer_email="test@example.com",
            reference="REF-123",
            credits_added=100,
            total_credits=500,
        )

        assert response.verified is True
        assert response.credits_added == 100

    def test_unverified_payment(self):
        """Test unverified payment response."""
        response = PaymentVerificationResponse(
            success=False,
            verified=False,
            error_message="Payment not found",
        )

        assert response.verified is False
        assert response.error_message is not None

    def test_optional_fields(self):
        """Test optional fields default to None."""
        response = PaymentVerificationResponse(
            success=True,
            verified=True,
        )

        assert response.amount is None
        assert response.currency is None
        assert response.paid_at is None


class TestPlanResponse:
    """Tests for PlanResponse schema."""

    def test_valid_pricing_package(self):
        """Test valid pricing package response."""
        package = PlanResponse(
            id=uuid4(),
            name="Pro Package",
            subtitle="Most Popular",
            price=29.99,
            credits=500,
            original_price=39.99,
            description="Best value for professionals",
            features=["Feature 1", "Feature 2", "Feature 3"],
            popular=True,
            cta="Get Started",
            highlight=True,
            savings=25.0,
        )

        assert package.name == "Pro Package"
        assert package.credits == 500
        assert package.popular is True
        assert len(package.features) == 3

    def test_optional_icon(self):
        """Test icon is optional."""
        package = PlanResponse(
            id=uuid4(),
            name="Basic",
            subtitle="Starter",
            price=9.99,
            credits=100,
            original_price=9.99,
            description="Entry level",
            features=["Basic feature"],
            popular=False,
            cta="Try Now",
            highlight=False,
            savings=0.0,
        )

        assert package.icon is None


class TestPaymentHistoryResponse:
    """Tests for PaymentHistoryResponse schema."""

    def test_valid_payment_history(self):
        """Test valid payment history item."""
        history = PaymentHistoryResponse(
            id="pay-123",
            plan_name="Pro Package",
            credits_purchased=500,
            amount=29.99,
            currency="USD",
            status="success",
            payment_method="card",
            provider="stripe",
            created_at=datetime.now(),
        )

        assert history.id == "pay-123"
        assert history.credits_purchased == 500
        assert history.status == "success"

    def test_completed_at_optional(self):
        """Test completed_at is optional."""
        history = PaymentHistoryResponse(
            id="pay-123",
            plan_name="Basic",
            credits_purchased=100,
            amount=9.99,
            currency="USD",
            status="pending",
            payment_method="bank_transfer",
            provider="paystack",
            created_at=datetime.now(),
        )

        assert history.completed_at is None


class TestCreditsOverviewResponse:
    """Tests for CreditsOverviewResponse schema."""

    def test_valid_credits_overview(self):
        """Test valid credits overview."""
        overview = CreditsOverviewResponse(
            current_balance=250,
            total_purchased=1000,
            total_used=750,
            total_spent=99.99,
            currency="USD",
            purchase_history=[],
        )

        assert overview.current_balance == 250
        assert overview.total_purchased == 1000
        assert overview.total_used == 750

    def test_with_purchase_history(self):
        """Test overview with purchase history."""
        history_item = PaymentHistoryResponse(
            id="pay-123",
            plan_name="Pro",
            credits_purchased=500,
            amount=29.99,
            currency="USD",
            status="success",
            payment_method="card",
            provider="stripe",
            created_at=datetime.now(),
        )

        overview = CreditsOverviewResponse(
            current_balance=500,
            total_purchased=500,
            total_used=0,
            total_spent=29.99,
            currency="USD",
            purchase_history=[history_item],
        )

        assert len(overview.purchase_history) == 1
        assert overview.purchase_history[0].plan_name == "Pro"
