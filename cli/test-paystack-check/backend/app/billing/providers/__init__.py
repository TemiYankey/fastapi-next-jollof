"""Payment providers."""

from app.billing.providers.paystack import PaystackProvider

__all__ = ["PaystackProvider"]

payment_provider = PaystackProvider()
