"""Stripe payment provider implementation."""

import hashlib
import hmac
import logging
import time
import uuid
from decimal import Decimal
from typing import Any, Dict, Optional

import stripe
from stripe.error import StripeError

from app.billing.providers.base import BasePaymentProvider
from app.billing.schemas import CheckoutResponse, PaymentVerificationResponse
from app.core.config import settings

logger = logging.getLogger(__name__)


class StripeProvider(BasePaymentProvider):
    """Stripe payment provider."""

    def __init__(self):
        """Initialize Stripe client."""
        stripe.api_key = settings.stripe_secret_key
        self.webhook_secret = settings.stripe_webhook_secret

    def generate_reference(self) -> str:
        """Generate a unique payment reference."""
        timestamp = int(time.time() * 1000)
        unique_id = uuid.uuid4().hex[:8]
        return f"stripe_{timestamp}_{unique_id}"

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
        """Create a Stripe checkout session."""
        try:
            reference = order_reference or self.generate_reference()

            # Stripe expects amount in cents
            amount_cents = int(amount * 100)

            session_metadata = {
                "order_reference": reference,
                "customer_name": customer_name,
                **(metadata or {}),
            }

            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": settings.stripe_currency,
                            "product_data": {
                                "name": metadata.get("plan_name", "Credits") if metadata else "Credits",
                            },
                            "unit_amount": amount_cents,
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=success_url + f"?reference={reference}",
                cancel_url=cancel_url or success_url,
                customer_email=customer_email,
                metadata=session_metadata,
            )

            logger.info(f"Stripe checkout session created: {session.id}, reference: {reference}")

            return CheckoutResponse(
                success=True,
                checkout_url=session.url,
                reference=reference,
                metadata={
                    "session_id": session.id,
                    "provider": "stripe",
                },
            )

        except StripeError as e:
            logger.error(f"Stripe checkout error: {e}")
            return CheckoutResponse(
                success=False,
                error_message=str(e),
            )
        except Exception as e:
            logger.error(f"Unexpected error creating Stripe checkout: {e}")
            return CheckoutResponse(
                success=False,
                error_message="Failed to create checkout session",
            )

    async def verify_payment(self, reference: str) -> PaymentVerificationResponse:
        """Verify payment by reference (session lookup)."""
        try:
            # List sessions and find by metadata reference
            sessions = stripe.checkout.Session.list(limit=100)

            for session in sessions.auto_paging_iter():
                if session.metadata.get("order_reference") == reference:
                    if session.payment_status == "paid":
                        # Get payment intent for more details
                        payment_intent = stripe.PaymentIntent.retrieve(session.payment_intent)

                        return PaymentVerificationResponse(
                            success=True,
                            verified=True,
                            status="success",
                            amount=Decimal(session.amount_total) / 100,
                            currency=session.currency.upper(),
                            payment_method=payment_intent.payment_method_types[0] if payment_intent.payment_method_types else "card",
                            paid_at=None,  # Stripe doesn't provide this directly
                            customer_email=session.customer_email,
                            reference=reference,
                            provider_reference=session.id,
                            raw_response={"session_id": session.id, "status": session.payment_status},
                        )
                    else:
                        return PaymentVerificationResponse(
                            success=True,
                            verified=False,
                            status=session.payment_status,
                            reference=reference,
                            message=f"Payment status: {session.payment_status}",
                        )

            return PaymentVerificationResponse(
                success=False,
                verified=False,
                error_message=f"No session found for reference: {reference}",
            )

        except StripeError as e:
            logger.error(f"Stripe verification error: {e}")
            return PaymentVerificationResponse(
                success=False,
                verified=False,
                error_message=str(e),
            )
        except Exception as e:
            logger.error(f"Unexpected error verifying Stripe payment: {e}")
            return PaymentVerificationResponse(
                success=False,
                verified=False,
                error_message="Failed to verify payment",
            )

    async def handle_webhook(self, payload: Dict[str, Any], signature: Optional[str] = None) -> Dict[str, Any]:
        """Handle Stripe webhook events."""
        try:
            if signature and self.webhook_secret:
                event = stripe.Webhook.construct_event(
                    payload=payload if isinstance(payload, (str, bytes)) else str(payload),
                    sig_header=signature,
                    secret=self.webhook_secret,
                )
            else:
                event = stripe.Event.construct_from(payload, stripe.api_key)

            event_type = event.type
            data = event.data.object

            logger.info(f"Stripe webhook received: {event_type}")

            if event_type == "checkout.session.completed":
                reference = data.metadata.get("order_reference")
                return {
                    "success": True,
                    "event_type": event_type,
                    "reference": reference,
                    "session_id": data.id,
                    "payment_status": data.payment_status,
                    "amount": data.amount_total / 100 if data.amount_total else None,
                    "customer_email": data.customer_email,
                }

            elif event_type == "payment_intent.succeeded":
                return {
                    "success": True,
                    "event_type": event_type,
                    "payment_intent_id": data.id,
                    "amount": data.amount / 100 if data.amount else None,
                    "status": data.status,
                }

            elif event_type == "payment_intent.payment_failed":
                return {
                    "success": True,
                    "event_type": event_type,
                    "payment_intent_id": data.id,
                    "error": data.last_payment_error.message if data.last_payment_error else "Unknown error",
                }

            return {
                "success": True,
                "event_type": event_type,
                "message": "Event received but not processed",
            }

        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Stripe webhook signature verification failed: {e}")
            return {
                "success": False,
                "error": "Invalid signature",
            }
        except Exception as e:
            logger.error(f"Stripe webhook error: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify Stripe webhook signature."""
        try:
            stripe.Webhook.construct_event(
                payload=payload,
                sig_header=signature,
                secret=self.webhook_secret,
            )
            return True
        except stripe.error.SignatureVerificationError:
            return False
