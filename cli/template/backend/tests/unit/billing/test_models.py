"""Tests for payment models."""

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
            plan_id="pkg-123",
            plan_name="Test Package",
            credits_purchased=100,
            amount=1000,
            reference="REF-123",
            status=PaymentStatus.PENDING,
        )

        result = str(payment)

        assert "REF-123" in result
        assert "PENDING" in result.upper() or "pending" in result.lower()

    def test_payment_table_name(self):
        """Test Payment model has correct table name."""
        assert Payment._meta.db_table == "payments"

    def test_payment_has_required_fields(self):
        """Test Payment model has required fields."""
        field_names = [f.model_field_name for f in Payment._meta.fields_map.values()]

        assert "id" in field_names
        assert "plan_id" in field_names
        assert "plan_name" in field_names
        assert "amount" in field_names
        assert "currency" in field_names
        assert "status" in field_names
        assert "reference" in field_names

    def test_payment_status_enum_values(self):
        """Test payment can use all status enum values."""
        for status in PaymentStatus:
            payment = Payment(
                id=uuid4(),
                plan_id="pkg-123",
                plan_name="Test Package",
                credits_purchased=100,
                amount=1000,
                reference=f"REF-{status.value}",
                status=status,
            )
            assert payment.status == status

    def test_payment_method_enum_values(self):
        """Test payment can use all method enum values."""
        for method in PaymentMethod:
            payment = Payment(
                id=uuid4(),
                plan_id="pkg-123",
                plan_name="Test Package",
                credits_purchased=100,
                amount=1000,
                reference=f"REF-{method.value}",
                payment_method=method,
            )
            assert payment.payment_method == method

    def test_payment_provider_enum_values(self):
        """Test payment can use all provider enum values."""
        for provider in PaymentProvider:
            payment = Payment(
                id=uuid4(),
                plan_id="pkg-123",
                plan_name="Test Package",
                credits_purchased=100,
                amount=1000,
                reference=f"REF-{provider.value}",
                provider=provider,
            )
            assert payment.provider == provider


class TestPlanModel:
    """Tests for Plan model."""

    def test_plan_str_representation(self):
        """Test plan string representation."""
        plan = Plan(
            id=uuid4(),
            name="Pro Package",
            price=2999,
        )

        result = str(plan)

        assert "Pro Package" in result

    def test_plan_table_name(self):
        """Test Plan model has correct table name."""
        assert Plan._meta.db_table == "plans"

    def test_plan_has_required_fields(self):
        """Test Plan model has required fields."""
        field_names = [f.model_field_name for f in Plan._meta.fields_map.values()]

        assert "id" in field_names
        assert "name" in field_names
        assert "price" in field_names
        assert "features" in field_names
        assert "popular" in field_names
        assert "is_active" in field_names

    def test_plan_with_all_fields(self):
        """Test plan with all fields set."""
        plan_id = uuid4()

        plan = Plan(
            id=plan_id,
            name="Enterprise",
            subtitle="Best Value",
            price=9999,
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

        assert plan.id == plan_id
        assert plan.name == "Enterprise"
        assert plan.subtitle == "Best Value"
        assert plan.price == 9999
        assert plan.popular is True
        assert plan.is_active is True
