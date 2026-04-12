"""Billing models."""

from tortoise import fields

from app.base.models import BaseModel
from app.billing.enums import PaymentMethod, PaymentProvider, PaymentStatus


class Payment(BaseModel):
    """Payment/transaction record supporting multiple providers."""

    user = fields.ForeignKeyField("users.User", related_name="payments")

    # Purchase details
    plan_id = fields.CharField(max_length=50)
    plan_name = fields.CharField(max_length=255)
    credits_purchased = fields.IntField()
    amount = fields.IntField()  # Stored in smallest currency unit (kobo/cents)
    currency = fields.CharField(max_length=3, default="NGN")
    status = fields.CharEnumField(
        PaymentStatus, max_length=20, default=PaymentStatus.PENDING
    )
    payment_method = fields.CharEnumField(
        PaymentMethod, max_length=20, default=PaymentMethod.CARD
    )
    provider = fields.CharEnumField(
        PaymentProvider, max_length=20, default=PaymentProvider.NOMBA
    )

    # Payment reference (internal)
    reference = fields.CharField(max_length=255, unique=True)

    # Provider-specific references
    provider_order_reference = fields.CharField(max_length=255, null=True)
    provider_payment_reference = fields.CharField(max_length=255, null=True)
    checkout_url = fields.TextField(null=True)

    # Metadata
    completed_at = fields.DatetimeField(null=True)
    raw_response = fields.JSONField(default=dict)

    class Meta:
        table = "payments"

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

    name = fields.CharField(max_length=100)
    subtitle = fields.CharField(max_length=255, null=True)
    price = fields.IntField()  # Stored in smallest currency unit
    credits = fields.IntField(default=0)
    original_price = fields.IntField(default=0)
    description = fields.TextField(null=True)
    icon = fields.CharField(max_length=100, null=True)
    features = fields.JSONField(default=list)
    popular = fields.BooleanField(default=False)
    cta = fields.CharField(max_length=100, default="Get Started")
    highlight = fields.BooleanField(default=False)
    savings = fields.IntField(default=0)
    is_active = fields.BooleanField(default=True)

    # For subscriptions (optional)
    billing_period = fields.CharField(max_length=20, null=True)  # 'monthly', 'yearly', 'one_time'

    class Meta:
        table = "plans"
        ordering = ["price"]

    def __str__(self) -> str:
        if self.credits > 0:
            return f"{self.name} ({self.credits} credits)"
        return f"{self.name}"
