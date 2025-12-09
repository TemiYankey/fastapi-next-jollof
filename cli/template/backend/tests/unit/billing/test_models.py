"""Tests for payment models."""

from decimal import Decimal
from uuid import uuid4

import pytest

from app.billing.enums import PaymentMethod, PaymentProvider, PaymentStatus
from app.billing.models import Payment, Plan


class TestPaymentModel:
    """Tests for Payment model."""

    def test_payment_str_representation(self):
        """Test payment string representation."""
        payment = Payment(
            id=uuid4(),
            user_id=uuid4(),
            plan_id="pkg-123",
            plan_name="Test Package",
            credits_purchased=100,
            amount=Decimal("10.00"),
            reference="REF-123",
            status=PaymentStatus.PENDING,
        )

        result = str(payment)

        assert "REF-123" in result
        # The status is stored as enum, so check for either format
        assert "PENDING" in result.upper() or "pending" in result.lower()

    def test_payment_column_defaults_defined(self):
        """Test payment model has defaults defined in column mapping."""
        # Note: SQLAlchemy defaults are applied at DB level, not in-memory.
        # Here we verify the default is defined in the column mapping.
        from sqlalchemy import inspect
        mapper = inspect(Payment)

        # Check currency column has default
        currency_col = mapper.columns['currency']
        assert currency_col.default is not None
        assert currency_col.default.arg == "NGN"

    def test_payment_with_explicit_defaults(self):
        """Test payment with explicit default values."""
        payment = Payment(
            id=uuid4(),
            user_id=uuid4(),
            plan_id="pkg-123",
            plan_name="Test Package",
            credits_purchased=100,
            amount=Decimal("10.00"),
            reference="REF-123",
            currency="NGN",
            status=PaymentStatus.PENDING,
            payment_method=PaymentMethod.CARD,
            provider=PaymentProvider.NOMBA,
        )

        assert payment.currency == "NGN"
        assert payment.status == PaymentStatus.PENDING
        assert payment.payment_method == PaymentMethod.CARD
        assert payment.provider == PaymentProvider.NOMBA

    def test_payment_status_enum_values(self):
        """Test payment can use all status enum values."""
        for status in PaymentStatus:
            payment = Payment(
                id=uuid4(),
                user_id=uuid4(),
                plan_id="pkg-123",
                plan_name="Test Package",
                credits_purchased=100,
                amount=Decimal("10.00"),
                reference=f"REF-{status.value}",
                status=status,
            )
            assert payment.status == status

    def test_payment_method_enum_values(self):
        """Test payment can use all method enum values."""
        for method in PaymentMethod:
            payment = Payment(
                id=uuid4(),
                user_id=uuid4(),
                plan_id="pkg-123",
                plan_name="Test Package",
                credits_purchased=100,
                amount=Decimal("10.00"),
                reference=f"REF-{method.value}",
                payment_method=method,
            )
            assert payment.payment_method == method

    def test_payment_provider_enum_values(self):
        """Test payment can use all provider enum values."""
        for provider in PaymentProvider:
            payment = Payment(
                id=uuid4(),
                user_id=uuid4(),
                plan_id="pkg-123",
                plan_name="Test Package",
                credits_purchased=100,
                amount=Decimal("10.00"),
                reference=f"REF-{provider.value}",
                provider=provider,
            )
            assert payment.provider == provider

    def test_payment_optional_fields(self):
        """Test payment optional fields default to None."""
        payment = Payment(
            id=uuid4(),
            user_id=uuid4(),
            plan_id="pkg-123",
            plan_name="Test Package",
            credits_purchased=100,
            amount=Decimal("10.00"),
            reference="REF-123",
        )

        assert payment.provider_order_reference is None
        assert payment.provider_payment_reference is None
        assert payment.checkout_url is None
        assert payment.completed_at is None

    def test_payment_raw_response_column_has_default(self):
        """Test raw_response column has default defined."""
        from sqlalchemy import inspect
        mapper = inspect(Payment)

        raw_response_col = mapper.columns['raw_response']
        assert raw_response_col.default is not None

    def test_payment_with_all_fields(self):
        """Test payment with all fields set."""
        user_id = uuid4()
        payment_id = uuid4()

        payment = Payment(
            id=payment_id,
            user_id=user_id,
            plan_id="pkg-pro",
            plan_name="Pro Package",
            credits_purchased=500,
            amount=Decimal("29.99"),
            currency="USD",
            status=PaymentStatus.SUCCESS,
            payment_method=PaymentMethod.BANK_TRANSFER,
            provider=PaymentProvider.PAYSTACK,
            reference="REF-456",
            provider_order_reference="ORD-123",
            provider_payment_reference="PAY-789",
            checkout_url="https://pay.example.com",
            raw_response={"key": "value"},
        )

        assert payment.id == payment_id
        assert payment.user_id == user_id
        assert payment.plan_id == "pkg-pro"
        assert payment.plan_name == "Pro Package"
        assert payment.credits_purchased == 500
        assert payment.amount == Decimal("29.99")
        assert payment.currency == "USD"
        assert payment.status == PaymentStatus.SUCCESS
        assert payment.payment_method == PaymentMethod.BANK_TRANSFER
        assert payment.provider == PaymentProvider.PAYSTACK


class TestPlanModel:
    """Tests for Plan model."""

    def test_pricing_package_str_representation(self):
        """Test pricing package string representation."""
        package = Plan(
            id=uuid4(),
            name="Pro Package",
            price=2999,
            credits=500,
            original_price=3999,
        )

        result = str(package)

        assert "Pro Package" in result
        assert "500 credits" in result

    def test_pricing_package_column_defaults_defined(self):
        """Test pricing package model has defaults defined in column mapping."""
        from sqlalchemy import inspect
        mapper = inspect(Plan)

        # Check various columns have defaults
        cta_col = mapper.columns['cta']
        assert cta_col.default is not None
        assert cta_col.default.arg == "Get Started"

        popular_col = mapper.columns['popular']
        assert popular_col.default is not None
        assert popular_col.default.arg is False

        is_active_col = mapper.columns['is_active']
        assert is_active_col.default is not None
        assert is_active_col.default.arg is True

    def test_pricing_package_with_explicit_defaults(self):
        """Test pricing package with explicit default values."""
        package = Plan(
            id=uuid4(),
            name="Basic",
            price=999,
            credits=100,
            original_price=999,
            features=[],
            popular=False,
            cta="Purchase",
            highlight=False,
            savings=0,
            is_active=True,
        )

        assert package.subtitle is None
        assert package.description is None
        assert package.icon is None
        assert package.features == []
        assert package.popular is False
        assert package.cta == "Purchase"
        assert package.highlight is False
        assert package.savings == 0
        assert package.is_active is True

    def test_pricing_package_with_all_fields(self):
        """Test pricing package with all fields set."""
        plan_id = uuid4()

        package = Plan(
            id=plan_id,
            name="Enterprise",
            subtitle="Best Value",
            price=9999,
            credits=2000,
            original_price=14999,
            description="For large teams",
            icon="building",
            features=["Priority support", "Custom limits", "API access"],
            popular=True,
            cta="Contact Sales",
            highlight=True,
            savings=33,
            is_active=True,
        )

        assert package.id == plan_id
        assert package.name == "Enterprise"
        assert package.subtitle == "Best Value"
        assert package.price == 9999
        assert package.credits == 2000
        assert package.original_price == 14999
        assert package.description == "For large teams"
        assert package.icon == "building"
        assert len(package.features) == 3
        assert "Priority support" in package.features
        assert package.popular is True
        assert package.cta == "Contact Sales"
        assert package.highlight is True
        assert package.savings == 33
        assert package.is_active is True

    def test_pricing_package_inactive(self):
        """Test inactive pricing package."""
        package = Plan(
            id=uuid4(),
            name="Deprecated",
            price=0,
            credits=0,
            original_price=0,
            is_active=False,
        )

        assert package.is_active is False


class TestPaymentTableName:
    """Tests for Payment table name."""

    def test_payment_tablename(self):
        """Test Payment model has correct table name."""
        assert Payment.__tablename__ == "payments"


class TestPlanTableName:
    """Tests for Plan table name."""

    def test_pricing_package_tablename(self):
        """Test Plan model has correct table name."""
        assert Plan.__tablename__ == "plans"
