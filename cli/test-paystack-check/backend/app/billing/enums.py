"""Payment enumerations."""

from enum import Enum


class PaymentStatus(str, Enum):
    """Payment status enumeration."""

    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class PaymentMethod(str, Enum):
    """Payment method enumeration."""

    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    UNKNOWN = "unknown"


class PaymentProvider(str, Enum):
    """Supported payment providers."""

    PAYSTACK = "paystack"
