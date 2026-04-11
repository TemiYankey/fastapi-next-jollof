"""Billing routes - Nomba provider (tested)."""

import hashlib
import hmac
import logging
import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.config import settings
from app.core.rate_limiter import (
    CHECKOUT_LIMIT,
    GENERAL_LIMIT,
    PAYMENT_LIMIT,
    PUBLIC_LIMIT,
    WEBHOOK_LIMIT,
    limiter,
)
from app.billing.enums import PaymentProvider, PaymentStatus
from app.billing.models import Payment, Plan
from app.billing.providers import nomba_provider
from app.billing.schemas import (
    CheckoutRequest,
    CheckoutResponse,
    CreditsOverviewResponse,
    PaymentHistoryResponse,
    PaymentVerificationResponse,
    PlanResponse,
)
from app.users.auth import get_current_user
from app.users.models import User

router = APIRouter(prefix="/billing", tags=["Billing"])
logger = logging.getLogger("app.billing")


def utcnow():
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def verify_nomba_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify Nomba webhook signature using HMAC-SHA512."""
    if not secret or not signature:
        return False
    expected_signature = hmac.new(
        secret.encode("utf-8"), payload, hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(signature.lower(), expected_signature.lower())


@router.post("/create-checkout", response_model=CheckoutResponse)
@limiter.limit(CHECKOUT_LIMIT)
async def create_checkout_session(
    request: Request,
    checkout_data: CheckoutRequest,
    current_user: User = Depends(get_current_user),
):
    """Create checkout session for plan purchase using Nomba."""
    reference = f"pay_{uuid.uuid4().hex[:12]}"

    nomba_response = await nomba_provider.create_checkout_session(
        amount=checkout_data.amount,
        customer_email=current_user.email,
        customer_name=current_user.full_name,
        success_url=checkout_data.success_url,
        cancel_url=checkout_data.cancel_url,
        order_reference=reference,
        metadata={
            "plan_id": checkout_data.plan_id,
            "plan_name": checkout_data.plan_name,
            "credits": checkout_data.credits,
            "user_id": str(current_user.id),
        },
    )

    if not nomba_response.success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the checkout session, please try again later.",
        )

    # Create payment record
    payment = await Payment.create(
        user=current_user,
        plan_id=checkout_data.plan_id,
        plan_name=checkout_data.plan_name,
        credits_purchased=checkout_data.credits,
        amount=checkout_data.amount,
        reference=reference,
        provider=PaymentProvider.NOMBA,
        provider_order_reference=nomba_response.reference or "",
        checkout_url=nomba_response.checkout_url or "",
        status=PaymentStatus.PENDING,
    )

    return CheckoutResponse(
        success=True,
        checkout_url=nomba_response.checkout_url,
        reference=reference,
        metadata={
            "payment_id": str(payment.id),
            "credits": checkout_data.credits,
        },
    )


@router.get("/verify/{reference}", response_model=PaymentVerificationResponse)
@limiter.limit(PAYMENT_LIMIT)
async def verify_payment(
    request: Request,
    reference: str,
    current_user: User = Depends(get_current_user),
):
    """
    Verify payment and add credits to user account.
    """
    payment = await Payment.filter(
        reference=reference, user=current_user
    ).first()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found"
        )

    # Idempotency: Skip if already successful
    if payment.status == PaymentStatus.SUCCESS:
        await current_user.refresh_from_db()
        return PaymentVerificationResponse(
            success=True,
            verified=True,
            status="success",
            credits_added=payment.credits_purchased,
            total_credits=current_user.credits,
            message="Credits already added to your account",
            reference=payment.reference,
            amount=payment.amount,
            currency=payment.currency,
            payment_method=payment.payment_method,
            paid_at=payment.completed_at,
        )

    # Skip if already failed
    if payment.status == PaymentStatus.FAILED:
        return PaymentVerificationResponse(
            success=False,
            verified=False,
            status="failed",
            error_message="This payment has failed. Please try again.",
            reference=payment.reference,
        )

    # Verify with Nomba
    verification = await nomba_provider.verify_payment(
        payment.provider_order_reference or reference
    )
    now = utcnow()

    if verification.success and verification.verified:
        # Update payment status
        payment.status = PaymentStatus.SUCCESS
        payment.completed_at = verification.paid_at or now
        payment.provider_payment_reference = verification.provider_reference or ""
        payment.raw_response = verification.raw_response or {}
        await payment.save()

        # Add credits to user account
        current_user.credits += payment.credits_purchased
        current_user.last_purchase_date = now
        await current_user.save()

        logger.info(
            f"Verification: Added {payment.credits_purchased} credits to user {current_user.id} "
            f"for payment {reference}"
        )

        return PaymentVerificationResponse(
            success=True,
            verified=True,
            status="success",
            credits_added=payment.credits_purchased,
            total_credits=current_user.credits,
            message=f"Successfully added {payment.credits_purchased} credits to your account",
            reference=payment.reference,
            amount=payment.amount,
            currency=payment.currency,
            payment_method=payment.payment_method,
            paid_at=payment.completed_at,
            customer_email=current_user.email,
            provider_reference=verification.provider_reference,
            raw_response=verification.raw_response,
        )

    return PaymentVerificationResponse(
        success=verification.success,
        verified=verification.verified,
        status=verification.status,
        error_message=verification.error_message,
    )


@router.get("/plans", response_model=List[PlanResponse])
@limiter.limit(PUBLIC_LIMIT)
async def get_plans(request: Request):
    """Get active billing plans."""
    plans = await Plan.filter(is_active=True).order_by("price").all()
    return plans


@router.get("/credits", response_model=CreditsOverviewResponse)
@limiter.limit(GENERAL_LIMIT)
async def get_credits_overview(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """Get comprehensive credits overview including balance and purchase history."""
    # Get all successful purchases
    successful_purchases = await Payment.filter(
        user=current_user, status=PaymentStatus.SUCCESS
    ).all()

    # Calculate totals
    total_purchased = sum(p.credits_purchased for p in successful_purchases)
    total_spent = sum(float(p.amount) for p in successful_purchases)

    # Get recent purchase history (last 20)
    recent_purchases = await Payment.filter(
        user=current_user
    ).order_by("-created_at").limit(20).all()

    return CreditsOverviewResponse(
        current_balance=current_user.credits,
        total_purchased=total_purchased,
        total_used=max(0, total_purchased - current_user.credits),
        total_spent=total_spent,
        currency="NGN",
        purchase_history=[
            PaymentHistoryResponse(
                id=str(purchase.id),
                plan_name=purchase.plan_name,
                credits_purchased=purchase.credits_purchased,
                amount=float(purchase.amount),
                currency=purchase.currency,
                status=purchase.status,
                payment_method=purchase.payment_method,
                provider=purchase.provider,
                created_at=purchase.created_at,
                completed_at=purchase.completed_at,
            )
            for purchase in recent_purchases
        ],
    )


@router.post("/webhook/nomba")
@limiter.limit(WEBHOOK_LIMIT)
async def nomba_webhook(request: Request):
    """
    Handle Nomba webhook with security and idempotency.

    Security measures:
    1. Signature verification (HMAC-SHA512)
    2. Idempotency check (only process PENDING payments)
    """
    body = await request.body()

    # Verify webhook signature
    signature = request.headers.get("X-Nomba-Signature", "")
    if settings.nomba_webhook_secret:
        if not verify_nomba_webhook_signature(
            body, signature, settings.nomba_webhook_secret
        ):
            logger.warning(
                f"Webhook signature verification failed. Signature: {signature[:20]}..."
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature",
            )
    else:
        logger.warning("Webhook secret not configured - skipping signature verification")

    try:
        payload = await request.json()
        result = await nomba_provider.handle_webhook(payload)

        if not result["success"] or not result["processed"]:
            logger.warning(f"Webhook processing returned unsuccessful: {result}")
            return {"status": "received", "processed": False}

        order_ref = result["order_reference"]
        if not order_ref:
            logger.warning("Webhook payload missing order reference")
            return {"status": "received", "processed": False}

        # Get payment
        payment = await Payment.filter(reference=order_ref).first()

        if not payment:
            logger.warning(f"Payment not found for reference: {order_ref}")
            return {"status": "received", "processed": False}

        # Idempotency check
        if payment.status != PaymentStatus.PENDING:
            logger.info(
                f"Payment {order_ref} already processed with status: {payment.status}. "
                "Skipping duplicate webhook."
            )
            return {"status": "received", "processed": False, "reason": "already_processed"}

        # Process based on payment status
        if result["status"] == "success":
            payment.status = PaymentStatus.SUCCESS
            payment.completed_at = utcnow()
            payment.provider_payment_reference = result.get("payment_reference", "")
            payment.raw_response = result.get("raw_payload", {})
            await payment.save()

            # Get user and add credits
            user = await User.filter(id=payment.user_id).first()
            if user:
                user.credits += payment.credits_purchased
                user.last_purchase_date = utcnow()
                await user.save()

            logger.info(
                f"Webhook: Added {payment.credits_purchased} credits to user {payment.user_id} "
                f"for payment {order_ref}"
            )

        elif result["status"] == "failed":
            payment.status = PaymentStatus.FAILED
            payment.raw_response = result.get("raw_payload", {})
            await payment.save()
            logger.info(f"Webhook: Payment {order_ref} marked as failed")

        return {"status": "received", "processed": True}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}", exc_info=True)
        return {"status": "error", "message": "Internal processing error"}
