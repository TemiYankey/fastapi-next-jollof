"""Email module supporting multiple providers (Resend, Brevo)."""

from app.emails.enums import EmailProvider, EmailType
from app.emails.schemas import EmailRequest, EmailResponse, TemplatedEmailRequest
from app.emails.service import (
    EmailService,
    send_email,
    send_password_reset_email,
    send_payment_success_email,
    send_verification_email,
    send_welcome_email,
)

__all__ = [
    "EmailProvider",
    "EmailType",
    "EmailRequest",
    "EmailResponse",
    "TemplatedEmailRequest",
    "EmailService",
    "send_email",
    "send_welcome_email",
    "send_password_reset_email",
    "send_verification_email",
    "send_payment_success_email",
]
