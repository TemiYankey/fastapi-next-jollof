"""Billing models using SQLAlchemy 2.0."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional
import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base.models import BaseModel
from app.billing.enums import PaymentMethod, PaymentProvider, PaymentStatus

if TYPE_CHECKING:
    from app.users.models import User


class Payment(BaseModel):
    """Payment/transaction record supporting multiple providers."""

    __tablename__ = "payments"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )

    # Purchase details
    plan_id: Mapped[str] = mapped_column(String(50))
    plan_name: Mapped[str] = mapped_column(String(255))
    credits_purchased: Mapped[int] = mapped_column(Integer)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    currency: Mapped[str] = mapped_column(String(3), default="NGN")
    status: Mapped[PaymentStatus] = mapped_column(
        String(20), default=PaymentStatus.PENDING
    )
    payment_method: Mapped[PaymentMethod] = mapped_column(
        String(20), default=PaymentMethod.CARD
    )
    provider: Mapped[PaymentProvider] = mapped_column(
        String(20), default=PaymentProvider.NOMBA
    )

    # Payment reference (internal)
    reference: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    # Provider-specific references
    provider_order_reference: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    provider_payment_reference: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    checkout_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metadata
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    raw_response: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="payments")

    def __str__(self) -> str:
        return f"Payment({self.reference}, {self.status})"


class Plan(BaseModel):
    """
    Billing plan model - flexible for credits, subscriptions, or one-time purchases.

    Can represent:
    - Credit packages (credits field)
    - Subscription tiers (with billing_period)
    - One-time purchases
    """

    __tablename__ = "plans"

    name: Mapped[str] = mapped_column(String(100))
    subtitle: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    price: Mapped[int] = mapped_column(Integer)  # stored in smallest currency unit
    credits: Mapped[int] = mapped_column(Integer, default=0)
    original_price: Mapped[int] = mapped_column(Integer)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    features: Mapped[list[str]] = mapped_column(JSON, default=list)
    popular: Mapped[bool] = mapped_column(Boolean, default=False)
    cta: Mapped[str] = mapped_column(String(100), default="Get Started")
    highlight: Mapped[bool] = mapped_column(Boolean, default=False)
    savings: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # For subscriptions (optional)
    billing_period: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )  # 'monthly', 'yearly', 'one_time'

    def __str__(self) -> str:
        if self.credits > 0:
            return f"{self.name} ({self.credits} credits)"
        return f"{self.name}"
