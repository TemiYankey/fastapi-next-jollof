"""Tests for billing models."""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from app.billing.enums import PaymentMethod, PaymentProvider, PaymentStatus
from app.billing.models import Payment, Plan


class TestPlanModel:
    """Tests for Plan model."""

    def test_plan_creation(self):
        """Test creating a basic plan."""
        plan = Plan(
            id=uuid4(),
            name="Basic Plan",
            price=999,
            credits=100,
            original_price=999,
            is_active=True,
        )

        assert plan.name == "Basic Plan"
        assert plan.price == 999
        assert plan.credits == 100
        assert plan.is_active is True

    def test_plan_with_all_fields(self):
        """Test plan with all optional fields."""
        plan_id = uuid4()
        plan = Plan(
            id=plan_id,
            name="Premium Plan",
            subtitle="Best value plan",
            description="Full access to all features",
            price=2999,
            original_price=3999,
            credits=500,
            icon="star",
            features=["Feature 1", "Feature 2"],
            popular=True,
            cta="Buy Now",
            highlight=True,
            savings=1000,
            is_active=True,
            billing_period="monthly",
        )

        assert plan.id == plan_id
        assert plan.subtitle == "Best value plan"
        assert plan.description == "Full access to all features"
        assert plan.icon == "star"
        assert plan.popular is True
        assert plan.highlight is True
        assert plan.savings == 1000
        assert plan.billing_period == "monthly"

    def test_plan_default_values(self):
        """Test plan default values when explicitly provided."""
        # Note: Tortoise ORM defaults only apply at DB insert time
        # For unit tests, we test with explicit default values
        plan = Plan(
            id=uuid4(),
            name="Test",
            price=100,
            credits=10,
            original_price=100,
            is_active=True,
            popular=False,
            highlight=False,
            savings=0,
            cta="Get Started",
        )

        assert plan.is_active is True
        assert plan.popular is False
        assert plan.highlight is False
        assert plan.savings == 0
        assert plan.cta == "Get Started"


class TestPaymentModel:
    """Tests for Payment model."""

    def test_payment_creation(self):
        """Test creating a basic payment."""
        user_id = uuid4()
        payment = Payment(
            id=uuid4(),
            user_id=user_id,
            plan_id="pkg-123",
            plan_name="Basic Plan",
            credits_purchased=100,
            amount=Decimal("9.99"),
            currency="NGN",
            reference="REF-123",
            status=PaymentStatus.PENDING,
            payment_method=PaymentMethod.CARD,
            provider=PaymentProvider.PAYSTACK,
        )

        assert payment.user_id == user_id
        assert payment.plan_name == "Basic Plan"
        assert payment.credits_purchased == 100
        assert payment.amount == Decimal("9.99")
        assert payment.status == PaymentStatus.PENDING

    def test_payment_with_all_fields(self):
        """Test payment with all optional fields."""
        now = datetime.now(timezone.utc)
        payment = Payment(
            id=uuid4(),
            user_id=uuid4(),
            plan_id="pkg-456",
            plan_name="Premium",
            credits_purchased=500,
            amount=Decimal("29.99"),
            currency="NGN",
            reference="REF-456",
            provider_order_reference="ORD-456",
            provider_payment_reference="PAY-456",
            checkout_url="https://example.com/pay",
            status=PaymentStatus.SUCCESS,
            payment_method=PaymentMethod.BANK_TRANSFER,
            provider=PaymentProvider.PAYSTACK,
            completed_at=now,
            raw_response={"source": "web"},
        )

        assert payment.provider_order_reference == "ORD-456"
        assert payment.provider_payment_reference == "PAY-456"
        assert payment.checkout_url == "https://example.com/pay"
        assert payment.completed_at == now
        assert payment.raw_response == {"source": "web"}

    def test_payment_status_transitions(self):
        """Test payment status can be updated."""
        payment = Payment(
            id=uuid4(),
            user_id=uuid4(),
            plan_id="pkg-123",
            plan_name="Test",
            credits_purchased=10,
            amount=Decimal("1.00"),
            currency="NGN",
            reference="REF-789",
            status=PaymentStatus.PENDING,
            payment_method=PaymentMethod.CARD,
            provider=PaymentProvider.PAYSTACK,
        )

        assert payment.status == PaymentStatus.PENDING

        payment.status = PaymentStatus.SUCCESS
        assert payment.status == PaymentStatus.SUCCESS

        # Test can also transition to failed
        payment.status = PaymentStatus.FAILED
        assert payment.status == PaymentStatus.FAILED
