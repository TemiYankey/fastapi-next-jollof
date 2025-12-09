"""Base payment provider interface."""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any, Dict, Optional

from app.billing.schemas import CheckoutResponse, PaymentVerificationResponse


class BasePaymentProvider(ABC):
    """Abstract base class for payment providers."""

    @abstractmethod
    async def create_checkout_session(
        self,
        amount: Decimal,
        customer_email: str,
        customer_name: str,
        success_url: str,
        cancel_url: Optional[str] = None,
        order_reference: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CheckoutResponse:
        """Create a checkout session for payment."""
        pass

    @abstractmethod
    async def verify_payment(self, reference: str) -> PaymentVerificationResponse:
        """Verify a payment by reference."""
        pass

    @abstractmethod
    async def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle webhook from payment provider."""
        pass

    @abstractmethod
    def generate_reference(self) -> str:
        """Generate a unique payment reference."""
        pass
