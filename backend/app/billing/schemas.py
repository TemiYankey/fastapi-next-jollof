"""Billing schemas for request/response validation."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import Field

from app.base.schemas import BaseAppSchema


class CheckoutRequest(BaseAppSchema):
    """Checkout session request."""

    plan_id: str
    plan_name: str
    amount: Decimal = Field(gt=0, description="Amount must be positive")
    credits: int = Field(ge=0, description="Credits for this purchase")
    success_url: str
    cancel_url: str


class CheckoutResponse(BaseAppSchema):
    """Checkout session response."""

    success: bool
    checkout_url: Optional[str] = None
    reference: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PaymentVerificationResponse(BaseAppSchema):
    """Payment verification response."""

    success: bool
    verified: bool
    status: Optional[str] = None
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    payment_method: Optional[str] = None
    paid_at: Optional[datetime] = None
    customer_email: Optional[str] = None
    reference: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    message: Optional[str] = None
    credits_added: Optional[int] = None
    total_credits: Optional[int] = None
    provider_reference: Optional[str] = None


class PlanResponse(BaseAppSchema):
    """Billing plan response."""

    id: uuid.UUID
    name: str
    subtitle: Optional[str] = None
    price: float
    credits: int
    original_price: float
    description: Optional[str] = None
    icon: Optional[str] = None
    features: List[str]
    popular: bool
    cta: str
    highlight: bool
    savings: float
    billing_period: Optional[str] = None


class PaymentHistoryResponse(BaseAppSchema):
    """Payment history item."""

    id: str
    plan_name: str
    credits_purchased: int
    amount: float
    currency: str
    status: str
    payment_method: str
    provider: str
    created_at: datetime
    completed_at: Optional[datetime] = None


class CreditsOverviewResponse(BaseAppSchema):
    """Credits overview response with balance and purchase history."""

    current_balance: int
    total_purchased: int
    total_used: int
    total_spent: float
    currency: str
    purchase_history: List[PaymentHistoryResponse]
