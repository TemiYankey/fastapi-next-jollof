"""Tests for billing enums."""

import pytest

from app.billing.enums import PaymentMethod, PaymentProvider, PaymentStatus


class TestPaymentProvider:
    """Tests for PaymentProvider enum."""

    def test_paystack_provider(self):
        """Test Paystack provider value."""
        assert PaymentProvider.PAYSTACK.value == "paystack"

    def test_all_providers_available(self):
        """Test all expected providers are available."""
        provider_values = {p.value for p in PaymentProvider}
        assert "paystack" in provider_values


class TestPaymentStatus:
    """Tests for PaymentStatus enum."""

    def test_pending_status(self):
        """Test pending status value."""
        assert PaymentStatus.PENDING.value == "pending"

    def test_success_status(self):
        """Test success status value."""
        assert PaymentStatus.SUCCESS.value == "success"

    def test_failed_status(self):
        """Test failed status value."""
        assert PaymentStatus.FAILED.value == "failed"

    def test_cancelled_status(self):
        """Test cancelled status value."""
        assert PaymentStatus.CANCELLED.value == "cancelled"

    def test_expired_status(self):
        """Test expired status value."""
        assert PaymentStatus.EXPIRED.value == "expired"

    def test_all_statuses_available(self):
        """Test all expected statuses are available."""
        status_values = {s.value for s in PaymentStatus}
        assert status_values == {"pending", "success", "failed", "cancelled", "expired"}


class TestPaymentMethod:
    """Tests for PaymentMethod enum."""

    def test_card_method(self):
        """Test card payment method."""
        assert PaymentMethod.CARD.value == "card"

    def test_bank_transfer_method(self):
        """Test bank transfer payment method."""
        assert PaymentMethod.BANK_TRANSFER.value == "bank_transfer"

    def test_unknown_method(self):
        """Test unknown payment method."""
        assert PaymentMethod.UNKNOWN.value == "unknown"

    def test_all_methods_available(self):
        """Test all expected methods are available."""
        method_values = {m.value for m in PaymentMethod}
        assert method_values == {"card", "bank_transfer", "unknown"}


class TestEnumComparisons:
    """Tests for enum comparison behavior."""

    def test_provider_equality_with_string(self):
        """Test provider can be compared with string."""
        assert PaymentProvider.PAYSTACK == "paystack"

    def test_status_equality_with_string(self):
        """Test status can be compared with string."""
        assert PaymentStatus.PENDING == "pending"
        assert PaymentStatus.SUCCESS == "success"
        assert PaymentStatus.FAILED == "failed"

    def test_method_equality_with_string(self):
        """Test method can be compared with string."""
        assert PaymentMethod.CARD == "card"
        assert PaymentMethod.BANK_TRANSFER == "bank_transfer"
