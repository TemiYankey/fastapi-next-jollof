"""Paystack payment provider implementation."""

import hashlib
import hmac
import logging
import time
import uuid
from decimal import Decimal
from typing import Any, Dict, Optional

import httpx

from app.billing.providers.base import BasePaymentProvider
from app.billing.schemas import CheckoutResponse, PaymentVerificationResponse
from app.core.config import settings

logger = logging.getLogger(__name__)


class PaystackProvider(BasePaymentProvider):
    """Paystack payment provider for African markets."""

    BASE_URL = "https://api.paystack.co"

    def __init__(self):
        """Initialize Paystack client."""
        self.secret_key = settings.paystack_secret_key
        self.public_key = settings.paystack_public_key
        self.webhook_secret = settings.paystack_webhook_secret
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

    def generate_reference(self) -> str:
        """Generate a unique payment reference."""
        timestamp = int(time.time() * 1000)
        unique_id = uuid.uuid4().hex[:8]
        return f"ps_{timestamp}_{unique_id}"

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
        """Create a Paystack checkout session (initialize transaction)."""
        try:
            reference = order_reference or self.generate_reference()

            # Paystack expects amount in kobo (smallest currency unit)
            amount_kobo = int(amount * 100)

            payload = {
                "email": customer_email,
                "amount": amount_kobo,
                "reference": reference,
                "callback_url": success_url,
                "metadata": {
                    "customer_name": customer_name,
                    "order_reference": reference,
                    "cancel_url": cancel_url,
                    **(metadata or {}),
                },
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.BASE_URL}/transaction/initialize",
                    json=payload,
                    headers=self.headers,
                    timeout=30.0,
                )

                data = response.json()

                if response.status_code == 200 and data.get("status"):
                    auth_url = data["data"]["authorization_url"]
                    access_code = data["data"]["access_code"]

                    logger.info(f"Paystack transaction initialized: {reference}")

                    return CheckoutResponse(
                        success=True,
                        checkout_url=auth_url,
                        reference=reference,
                        metadata={
                            "access_code": access_code,
                            "provider": "paystack",
                        },
                    )
                else:
                    error_msg = data.get("message", "Failed to initialize transaction")
                    logger.error(f"Paystack initialization failed: {error_msg}")
                    return CheckoutResponse(
                        success=False,
                        error_message=error_msg,
                    )

        except httpx.RequestError as e:
            logger.error(f"Paystack request error: {e}")
            return CheckoutResponse(
                success=False,
                error_message="Network error communicating with Paystack",
            )
        except Exception as e:
            logger.error(f"Unexpected error creating Paystack checkout: {e}")
            return CheckoutResponse(
                success=False,
                error_message="Failed to create checkout session",
            )

    async def verify_payment(self, reference: str) -> PaymentVerificationResponse:
        """Verify payment by reference."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/transaction/verify/{reference}",
                    headers=self.headers,
                    timeout=30.0,
                )

                data = response.json()

                if response.status_code == 200 and data.get("status"):
                    transaction = data["data"]
                    status = transaction.get("status", "").lower()

                    if status == "success":
                        return PaymentVerificationResponse(
                            success=True,
                            verified=True,
                            status="success",
                            amount=Decimal(transaction.get("amount", 0)) / 100,
                            currency=transaction.get("currency", "NGN").upper(),
                            payment_method=transaction.get("channel", "card"),
                            paid_at=transaction.get("paid_at"),
                            customer_email=transaction.get("customer", {}).get("email"),
                            reference=reference,
                            provider_reference=str(transaction.get("id")),
                            raw_response=transaction,
                        )
                    else:
                        return PaymentVerificationResponse(
                            success=True,
                            verified=False,
                            status=status,
                            reference=reference,
                            message=f"Payment status: {status}",
                            raw_response=transaction,
                        )
                else:
                    error_msg = data.get("message", "Verification failed")
                    return PaymentVerificationResponse(
                        success=False,
                        verified=False,
                        error_message=error_msg,
                    )

        except httpx.RequestError as e:
            logger.error(f"Paystack verification request error: {e}")
            return PaymentVerificationResponse(
                success=False,
                verified=False,
                error_message="Network error verifying payment",
            )
        except Exception as e:
            logger.error(f"Unexpected error verifying Paystack payment: {e}")
            return PaymentVerificationResponse(
                success=False,
                verified=False,
                error_message="Failed to verify payment",
            )

    async def handle_webhook(self, payload: Dict[str, Any], signature: Optional[str] = None) -> Dict[str, Any]:
        """Handle Paystack webhook events."""
        try:
            event = payload.get("event", "")
            data = payload.get("data", {})

            logger.info(f"Paystack webhook received: {event}")

            if event == "charge.success":
                reference = data.get("reference")
                amount = data.get("amount", 0) / 100
                customer = data.get("customer", {})

                return {
                    "success": True,
                    "event_type": event,
                    "reference": reference,
                    "amount": amount,
                    "currency": data.get("currency", "NGN"),
                    "customer_email": customer.get("email"),
                    "status": "success",
                    "transaction_id": data.get("id"),
                }

            elif event == "transfer.success":
                return {
                    "success": True,
                    "event_type": event,
                    "reference": data.get("reference"),
                    "amount": data.get("amount", 0) / 100,
                    "status": "success",
                }

            elif event == "transfer.failed":
                return {
                    "success": True,
                    "event_type": event,
                    "reference": data.get("reference"),
                    "reason": data.get("reason"),
                    "status": "failed",
                }

            return {
                "success": True,
                "event_type": event,
                "message": "Event received but not processed",
            }

        except Exception as e:
            logger.error(f"Paystack webhook error: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify Paystack webhook signature."""
        if not self.webhook_secret:
            logger.warning("Paystack webhook secret not configured")
            return False

        computed_hash = hmac.new(
            self.webhook_secret.encode("utf-8"),
            payload,
            hashlib.sha512,
        ).hexdigest()

        return hmac.compare_digest(computed_hash, signature)

    async def list_banks(self, country: str = "nigeria") -> Dict[str, Any]:
        """List available banks for transfers."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/bank",
                    params={"country": country},
                    headers=self.headers,
                    timeout=30.0,
                )

                data = response.json()

                if response.status_code == 200 and data.get("status"):
                    return {
                        "success": True,
                        "banks": data["data"],
                    }
                else:
                    return {
                        "success": False,
                        "error": data.get("message", "Failed to list banks"),
                    }

        except Exception as e:
            logger.error(f"Error listing banks: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def resolve_account(self, account_number: str, bank_code: str) -> Dict[str, Any]:
        """Resolve bank account details."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/bank/resolve",
                    params={
                        "account_number": account_number,
                        "bank_code": bank_code,
                    },
                    headers=self.headers,
                    timeout=30.0,
                )

                data = response.json()

                if response.status_code == 200 and data.get("status"):
                    return {
                        "success": True,
                        "account_name": data["data"]["account_name"],
                        "account_number": data["data"]["account_number"],
                    }
                else:
                    return {
                        "success": False,
                        "error": data.get("message", "Failed to resolve account"),
                    }

        except Exception as e:
            logger.error(f"Error resolving account: {e}")
            return {
                "success": False,
                "error": str(e),
            }
