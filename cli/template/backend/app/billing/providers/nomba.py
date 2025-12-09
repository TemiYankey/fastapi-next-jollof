"""Nomba payment provider implementation."""

import logging
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, Optional

import httpx

from app.base.datetime import utcnow
from app.core.config import settings
from app.billing.providers.base import BasePaymentProvider
from app.billing.schemas import CheckoutResponse, PaymentVerificationResponse

logger = logging.getLogger("app.billing.nomba")


class NombaAPIException(Exception):
    """Exception raised for Nomba API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(message)


class NombaPaymentProvider(BasePaymentProvider):
    """Nomba payment provider implementation."""

    BASE_URL = "https://api.nomba.com/v1"

    def __init__(self):
        """Initialize Nomba provider."""
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._client_id = settings.nomba_client_id
        self._client_secret = settings.nomba_client_secret
        self._account_id = settings.nomba_account_id

    async def _get_access_token(self, refetch: bool = False) -> str:
        """Get or refresh access token."""
        if (
            self._access_token
            and self._token_expires_at
            and utcnow() < self._token_expires_at
            and not refetch
        ):
            return self._access_token

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.BASE_URL}/auth/token/issue",
                    json={
                        "client_id": self._client_id,
                        "client_secret": self._client_secret,
                        "grant_type": "client_credentials",
                    },
                    headers={
                        "Content-Type": "application/json",
                        "accountId": self._account_id,
                    },
                    timeout=30.0,
                )

                if response.status_code != 200:
                    raise NombaAPIException(
                        f"Token request failed: {response.status_code}",
                        response.status_code,
                        response.json() if response.content else None,
                    )

                token_data = response.json()
                self._access_token = token_data.get("data", {}).get("access_token")

                if not self._access_token:
                    raise NombaAPIException(
                        "Token request successful but no access token returned"
                    )

                expires_in = token_data.get("expires_in", 3600)
                self._token_expires_at = utcnow() + timedelta(seconds=expires_in - 60)

                return self._access_token

            except httpx.RequestError as e:
                raise NombaAPIException(f"Network error during token request: {str(e)}")

    async def _make_authenticated_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make authenticated request to Nomba API."""
        try:
            access_token = await self._get_access_token()
        except Exception as e:
            logger.error(f"Error getting access token: {e}")
            raise NombaAPIException(f"Error getting access token: {e}")

        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "accountId": self._account_id,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method.upper(),
                    url=url,
                    json=data,
                    params=params,
                    headers=headers,
                    timeout=60.0,
                )

                try:
                    response_data = response.json()
                except Exception:
                    response_data = {"raw_response": response.text, "code": ""}

                if response.status_code == 400:
                    error_message = response_data.get(
                        "message", "Bad Request - Invalid parameters"
                    )
                    raise NombaAPIException(
                        error_message, response.status_code, response_data
                    )
                elif response.status_code == 401:
                    error_message = response_data.get(
                        "message", "Unauthorized - Invalid authentication"
                    )
                    raise NombaAPIException(
                        error_message, response.status_code, response_data
                    )
                elif response.status_code == 404:
                    error_message = response_data.get(
                        "message", "Transaction not found"
                    )
                    raise NombaAPIException(
                        error_message, response.status_code, response_data
                    )
                elif response.status_code not in [200, 201]:
                    error_message = response_data.get(
                        "message", f"HTTP {response.status_code}"
                    )
                    raise NombaAPIException(
                        f"API request failed: {error_message}",
                        response.status_code,
                        response_data,
                    )

                nomba_code = response_data.get("code", "")
                if nomba_code and nomba_code != "00":
                    nomba_description = response_data.get("description", "")
                    raise NombaAPIException(
                        f"Nomba error: {nomba_description}",
                        response.status_code,
                        response_data,
                    )

                return response_data

            except httpx.RequestError as e:
                raise NombaAPIException(f"Network error: {str(e)}")

    def generate_reference(self) -> str:
        """Generate unique payment reference."""
        timestamp = utcnow().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"PAY-{timestamp}-{unique_id}"

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
        """Create checkout session with Nomba."""
        try:
            logger.info(
                f"Creating Nomba checkout session for {customer_email}, amount: {amount}"
            )

            reference = order_reference or self.generate_reference()
            amount_str = str(amount)

            nomba_data = {
                "order": {
                    "orderReference": reference,
                    "customerId": customer_email,
                    "customerEmail": customer_email,
                    "amount": amount_str,
                    "currency": "NGN",
                    "accountId": self._account_id,
                    "callbackUrl": success_url,
                    "redirectUrl": success_url,
                },
                "tokenizeCard": "false",
            }

            if metadata:
                nomba_data["order"]["metadata"] = metadata

            response_data = await self._make_authenticated_request(
                method="POST",
                endpoint="/checkout/order",
                data=nomba_data,
            )

            data = response_data.get("data", {})
            checkout_link = data.get("checkoutLink")

            return CheckoutResponse(
                success=True,
                checkout_url=checkout_link,
                reference=reference,
                metadata={
                    "nomba_status": response_data.get("status"),
                    "nomba_description": response_data.get("description"),
                },
            )

        except NombaAPIException as e:
            logger.error(f"Nomba API error: {e.message}", exc_info=True)
            return CheckoutResponse(
                success=False,
                error_message=f"Payment setup failed: {e.message}",
                metadata={"api_error": e.response_data},
            )
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return CheckoutResponse(
                success=False, error_message=f"Payment setup failed: {str(e)}"
            )

    async def verify_payment(self, reference: str) -> PaymentVerificationResponse:
        """Verify payment with Nomba using order reference."""
        try:
            response_data = await self._make_authenticated_request(
                method="GET",
                endpoint="/checkout/transaction",
                params={"idType": "ORDER_REFERENCE", "id": reference},
            )

            data = response_data.get("data", {})
            order_data = data.get("order", {})
            transaction_details = data.get("transactionDetails", {})

            payment_method = None
            if data.get("cardDetails"):
                payment_method = "card"
            elif data.get("transferDetails"):
                payment_method = "bank_transfer"

            transaction_verified = data.get("success") is True
            transaction_status = (
                "success" if transaction_verified else data.get("status", "pending")
            )

            return PaymentVerificationResponse(
                success=True,
                verified=transaction_verified,
                status=transaction_status,
                amount=Decimal(str(order_data.get("amount", "0.00"))),
                currency=order_data.get("currency", "NGN"),
                payment_method=payment_method,
                paid_at=transaction_details.get("transactionDate"),
                customer_email=order_data.get("customerEmail"),
                provider_reference=transaction_details.get("paymentReference"),
                reference=reference,
                raw_response=response_data,
            )

        except NombaAPIException as e:
            user_friendly_message = e.message
            if e.status_code == 404:
                user_friendly_message = (
                    "Payment not found. Please check your reference."
                )
            elif e.status_code == 401:
                user_friendly_message = (
                    "Unable to verify payment due to authentication error."
                )

            return PaymentVerificationResponse(
                success=False,
                verified=False,
                error_message=user_friendly_message,
                raw_response=e.response_data or {},
            )
        except Exception as e:
            return PaymentVerificationResponse(
                success=False,
                verified=False,
                error_message=f"Verification error: {str(e)}",
                raw_response={},
            )

    async def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Nomba webhook."""
        try:
            order_reference = payload.get("orderReference")
            payment_reference = payload.get("paymentReference")
            status = payload.get("status", "failed")
            amount_str = payload.get("amount", "0.00")

            amount = Decimal(str(amount_str))
            internal_status = self._map_status(status)

            return {
                "success": True,
                "processed": True,
                "order_reference": order_reference,
                "payment_reference": payment_reference,
                "status": internal_status,
                "amount": amount,
                "currency": "NGN",
                "payment_method": payload.get("paymentMethod"),
                "customer_email": payload.get("customerEmail"),
                "paid_at": payload.get("paidAt"),
                "metadata": payload.get("metadata", {}),
                "raw_payload": payload,
            }

        except Exception as e:
            return {
                "success": False,
                "processed": False,
                "error": f"Webhook processing error: {str(e)}",
                "raw_payload": payload,
            }

    def _map_status(self, nomba_status: str) -> str:
        """Map Nomba status to internal status."""
        status_mapping = {
            "success": "success",
            "successful": "success",
            "completed": "success",
            "failed": "failed",
            "failure": "failed",
            "cancelled": "cancelled",
            "canceled": "cancelled",
            "pending": "pending",
            "processing": "pending",
        }
        return status_mapping.get(nomba_status.lower(), "pending")


# Global instance
nomba_provider = NombaPaymentProvider()
