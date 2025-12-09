"""Payment enumerations."""

from enum import Enum


class PaymentStatus(str, Enum):
    """Payment status enumeration."""

    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    """Payment method enumeration."""

    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    USSD = "ussd"
    QR = "qr"


class PaymentProvider(str, Enum):
    """Supported payment providers."""

    NOMBA = "nomba"
    PAYSTACK = "paystack"
    STRIPE = "stripe"
