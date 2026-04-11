"""Tests for payment enumerations."""

from app.billing.enums import PaymentMethod, PaymentProvider, PaymentStatus


class TestPaymentStatus:
    """Tests for PaymentStatus enum."""

    def test_pending_status(self):
        """Test pending status value."""
        assert PaymentStatus.PENDING == "pending"
        assert PaymentStatus.PENDING.value == "pending"

    def test_success_status(self):
        """Test success status value."""
        assert PaymentStatus.SUCCESS == "success"
        assert PaymentStatus.SUCCESS.value == "success"

    def test_failed_status(self):
        """Test failed status value."""
        assert PaymentStatus.FAILED == "failed"
        assert PaymentStatus.FAILED.value == "failed"

    def test_cancelled_status(self):
        """Test cancelled status value."""
        assert PaymentStatus.CANCELLED == "cancelled"
        assert PaymentStatus.CANCELLED.value == "cancelled"

    def test_expired_status(self):
        """Test expired status value."""
        assert PaymentStatus.EXPIRED == "expired"
        assert PaymentStatus.EXPIRED.value == "expired"

    def test_status_is_string_enum(self):
        """Test that status values are strings."""
        for status in PaymentStatus:
            assert isinstance(status.value, str)

    def test_all_statuses_available(self):
        """Test all expected statuses exist."""
        expected = {"pending", "success", "failed", "cancelled", "expired"}
        actual = {s.value for s in PaymentStatus}
        assert actual == expected


class TestPaymentMethod:
    """Tests for PaymentMethod enum."""

    def test_card_method(self):
        """Test card payment method."""
        assert PaymentMethod.CARD == "card"
        assert PaymentMethod.CARD.value == "card"

    def test_bank_transfer_method(self):
        """Test bank transfer payment method."""
        assert PaymentMethod.BANK_TRANSFER == "bank_transfer"
        assert PaymentMethod.BANK_TRANSFER.value == "bank_transfer"

    def test_unknown_method(self):
        """Test unknown payment method."""
        assert PaymentMethod.UNKNOWN == "unknown"
        assert PaymentMethod.UNKNOWN.value == "unknown"

    def test_method_is_string_enum(self):
        """Test that method values are strings."""
        for method in PaymentMethod:
            assert isinstance(method.value, str)

    def test_all_methods_available(self):
        """Test all expected methods exist."""
        expected = {"card", "bank_transfer", "unknown"}
        actual = {m.value for m in PaymentMethod}
        assert actual == expected


class TestPaymentProvider:
    """Tests for PaymentProvider enum."""

    def test_nomba_provider(self):
        """Test Nomba provider value."""
        assert PaymentProvider.NOMBA == "nomba"
        assert PaymentProvider.NOMBA.value == "nomba"

    def test_stripe_provider(self):
        """Test Stripe provider value."""
        assert PaymentProvider.STRIPE == "stripe"
        assert PaymentProvider.STRIPE.value == "stripe"

    def test_provider_is_string_enum(self):
        """Test that provider values are strings."""
        for provider in PaymentProvider:
            assert isinstance(provider.value, str)

    def test_all_providers_available(self):
        """Test all expected providers exist."""
        expected = {"nomba", "stripe"}
        actual = {p.value for p in PaymentProvider}
        assert actual == expected


class TestEnumComparisons:
    """Tests for enum comparison operations."""

    def test_status_equality_with_string(self):
        """Test status can be compared with string."""
        assert PaymentStatus.SUCCESS == "success"
        assert PaymentStatus.PENDING != "success"

    def test_method_equality_with_string(self):
        """Test method can be compared with string."""
        assert PaymentMethod.CARD == "card"
        assert PaymentMethod.BANK_TRANSFER != "card"

    def test_provider_equality_with_string(self):
        """Test provider can be compared with string."""
        assert PaymentProvider.NOMBA == "nomba"
        assert PaymentProvider.STRIPE != "nomba"

    def test_enum_in_list_check(self):
        """Test enum membership in list."""
        valid_statuses = [PaymentStatus.SUCCESS, PaymentStatus.PENDING]
        assert PaymentStatus.SUCCESS in valid_statuses
        assert PaymentStatus.FAILED not in valid_statuses
