"""Email enumerations."""

from enum import Enum


class EmailProvider(str, Enum):
    """Supported email providers."""

    RESEND = "resend"
    BREVO = "brevo"


class EmailType(str, Enum):
    """Email template types."""

    WELCOME = "welcome"
    PASSWORD_RESET = "password_reset"
    EMAIL_VERIFICATION = "email_verification"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    GENERIC = "generic"
