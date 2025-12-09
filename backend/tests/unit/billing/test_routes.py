"""Tests for payment routes."""

import hashlib
import hmac
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.billing.enums import PaymentProvider, PaymentStatus
from app.billing.routes import verify_nomba_webhook_signature


class TestVerifyNombaWebhookSignature:
    """Tests for verify_nomba_webhook_signature function."""

    def test_valid_signature(self):
        """Test valid webhook signature verification."""
        payload = b'{"orderReference": "123"}'
        secret = "test-secret"

        # Generate valid signature
        expected_signature = hmac.new(
            secret.encode("utf-8"), payload, hashlib.sha512
        ).hexdigest()

        result = verify_nomba_webhook_signature(payload, expected_signature, secret)

        assert result is True

    def test_invalid_signature(self):
        """Test invalid webhook signature verification."""
        payload = b'{"orderReference": "123"}'
        secret = "test-secret"
        invalid_signature = "invalid-signature"

        result = verify_nomba_webhook_signature(payload, invalid_signature, secret)

        assert result is False

    def test_empty_secret(self):
        """Test signature verification with empty secret."""
        payload = b'{"orderReference": "123"}'
        signature = "some-signature"

        result = verify_nomba_webhook_signature(payload, signature, "")

        assert result is False

    def test_empty_signature(self):
        """Test signature verification with empty signature."""
        payload = b'{"orderReference": "123"}'
        secret = "test-secret"

        result = verify_nomba_webhook_signature(payload, "", secret)

        assert result is False

    def test_signature_case_insensitive(self):
        """Test signature verification is case insensitive."""
        payload = b'{"orderReference": "123"}'
        secret = "test-secret"

        expected_signature = hmac.new(
            secret.encode("utf-8"), payload, hashlib.sha512
        ).hexdigest()

        # Test uppercase
        result = verify_nomba_webhook_signature(payload, expected_signature.upper(), secret)

        assert result is True


class TestCreateCheckoutSession:
    """Tests for create_checkout_session endpoint."""

    @pytest.mark.asyncio
    async def test_successful_checkout_creation(self):
        """Test successful checkout session creation."""
        from app.billing.routes import create_checkout_session

        mock_user = MagicMock()
        mock_user.id = uuid4()
        mock_user.email = "test@example.com"
        mock_user.full_name = "Test User"

        mock_db = AsyncMock()
        mock_request = MagicMock()

        checkout_data = MagicMock()
        checkout_data.plan_id = "pkg-123"
        checkout_data.plan_name = "Test Package"
        checkout_data.amount = Decimal("10.00")
        checkout_data.credits = 100
        checkout_data.success_url = "https://example.com/success"
        checkout_data.cancel_url = "https://example.com/cancel"

        with patch("app.billing.routes.nomba_provider") as mock_provider:
            mock_provider.create_checkout_session = AsyncMock(
                return_value=MagicMock(
                    success=True,
                    checkout_url="https://checkout.nomba.com/pay/123",
                    reference="REF-123",
                )
            )

            result = await create_checkout_session(
                request=mock_request,
                checkout_data=checkout_data,
                current_user=mock_user,
                db=mock_db,
            )

            assert result.success is True
            assert result.checkout_url == "https://checkout.nomba.com/pay/123"
            mock_db.add.assert_called_once()
            mock_db.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_checkout_provider_failure(self):
        """Test checkout session handles provider failure."""
        from app.billing.routes import create_checkout_session

        mock_user = MagicMock()
        mock_user.id = uuid4()
        mock_user.email = "test@example.com"
        mock_user.full_name = "Test User"

        mock_db = AsyncMock()
        mock_request = MagicMock()

        checkout_data = MagicMock()
        checkout_data.plan_id = "pkg-123"
        checkout_data.plan_name = "Test Package"
        checkout_data.amount = Decimal("10.00")
        checkout_data.credits = 100
        checkout_data.success_url = "https://example.com/success"
        checkout_data.cancel_url = "https://example.com/cancel"

        with patch("app.billing.routes.nomba_provider") as mock_provider:
            mock_provider.create_checkout_session = AsyncMock(
                return_value=MagicMock(success=False)
            )

            with pytest.raises(HTTPException) as exc:
                await create_checkout_session(
                    request=mock_request,
                    checkout_data=checkout_data,
                    current_user=mock_user,
                    db=mock_db,
                )

            assert exc.value.status_code == 500


class TestVerifyPayment:
    """Tests for verify_payment endpoint."""

    @pytest.mark.asyncio
    async def test_payment_not_found(self):
        """Test verify payment when payment not found."""
        from app.billing.routes import verify_payment

        mock_user = MagicMock()
        mock_user.id = uuid4()

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        mock_request = MagicMock()

        with pytest.raises(HTTPException) as exc:
            await verify_payment(
                request=mock_request,
                reference="INVALID-REF",
                current_user=mock_user,
                db=mock_db,
            )

        assert exc.value.status_code == 404
        assert "not found" in exc.value.detail.lower()

    @pytest.mark.asyncio
    async def test_already_successful_payment(self):
        """Test verify payment that's already successful."""
        from app.billing.routes import verify_payment

        mock_user = MagicMock()
        mock_user.id = uuid4()
        mock_user.credits = 500

        mock_payment = MagicMock()
        mock_payment.status = PaymentStatus.SUCCESS
        mock_payment.credits_purchased = 100
        mock_payment.reference = "REF-123"
        mock_payment.amount = Decimal("10.00")
        mock_payment.currency = "NGN"
        mock_payment.payment_method = "card"
        mock_payment.completed_at = None

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_payment
        mock_db.execute = AsyncMock(return_value=mock_result)

        mock_request = MagicMock()

        result = await verify_payment(
            request=mock_request,
            reference="REF-123",
            current_user=mock_user,
            db=mock_db,
        )

        assert result.success is True
        assert result.verified is True
        assert "already added" in result.message.lower()

    @pytest.mark.asyncio
    async def test_already_failed_payment(self):
        """Test verify payment that's already failed."""
        from app.billing.routes import verify_payment

        mock_user = MagicMock()
        mock_user.id = uuid4()

        mock_payment = MagicMock()
        mock_payment.status = PaymentStatus.FAILED
        mock_payment.reference = "REF-123"

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_payment
        mock_db.execute = AsyncMock(return_value=mock_result)

        mock_request = MagicMock()

        result = await verify_payment(
            request=mock_request,
            reference="REF-123",
            current_user=mock_user,
            db=mock_db,
        )

        assert result.success is False
        assert result.verified is False
        assert "failed" in result.error_message.lower()

    @pytest.mark.asyncio
    async def test_successful_verification_adds_credits(self):
        """Test successful verification adds credits to user."""
        from app.billing.routes import verify_payment

        mock_user = MagicMock()
        mock_user.id = uuid4()
        mock_user.credits = 100
        mock_user.email = "test@example.com"

        mock_payment = MagicMock()
        mock_payment.status = PaymentStatus.PENDING
        mock_payment.credits_purchased = 50
        mock_payment.reference = "REF-123"
        mock_payment.provider_order_reference = "ORD-123"
        mock_payment.amount = Decimal("10.00")
        mock_payment.currency = "NGN"
        mock_payment.payment_method = "card"

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_payment
        mock_db.execute = AsyncMock(return_value=mock_result)

        mock_request = MagicMock()

        with patch("app.billing.routes.nomba_provider") as mock_provider:
            mock_provider.verify_payment = AsyncMock(
                return_value=MagicMock(
                    success=True,
                    verified=True,
                    paid_at=None,
                    provider_reference="PAY-123",
                    raw_response={},
                )
            )

            result = await verify_payment(
                request=mock_request,
                reference="REF-123",
                current_user=mock_user,
                db=mock_db,
            )

            assert result.success is True
            assert result.verified is True
            assert result.credits_added == 50
            assert mock_user.credits == 150  # 100 + 50


class TestGetPlans:
    """Tests for get_plans endpoint."""

    @pytest.mark.asyncio
    async def test_returns_active_packages(self):
        """Test returns only active pricing packages."""
        from app.billing.routes import get_plans
        from app.billing.models import Plan

        # Create real Plan objects
        pkg1 = Plan(
            id=uuid4(),
            name="Basic",
            price=999,
            credits=100,
            original_price=999,
            is_active=True,
        )
        pkg2 = Plan(
            id=uuid4(),
            name="Pro",
            price=2999,
            credits=500,
            original_price=2999,
            is_active=True,
        )
        mock_packages = [pkg1, pkg2]

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_packages
        mock_db.execute = AsyncMock(return_value=mock_result)

        mock_request = MagicMock()

        result = await get_plans(request=mock_request, db=mock_db)

        assert len(result) == 2
        assert result[0].name == "Basic"
        assert result[1].name == "Pro"


class TestGetCreditsOverview:
    """Tests for get_credits_overview endpoint."""

    @pytest.mark.asyncio
    async def test_returns_credits_overview(self):
        """Test returns user credits overview."""
        from datetime import datetime, timezone
        from app.billing.routes import get_credits_overview
        from app.billing.models import Payment
        from app.billing.enums import PaymentMethod, PaymentProvider

        mock_user = MagicMock()
        mock_user.id = uuid4()
        mock_user.credits = 250

        now = datetime.now(timezone.utc)

        # Create real Payment objects
        payment1 = Payment(
            id=uuid4(),
            user_id=mock_user.id,
            plan_id="pkg-1",
            plan_name="Basic",
            credits_purchased=100,
            amount=Decimal("9.99"),
            currency="NGN",
            reference="REF-1",
            status=PaymentStatus.SUCCESS,
            payment_method=PaymentMethod.CARD,
            provider=PaymentProvider.NOMBA,
            created_at=now,
            completed_at=now,
        )
        payment2 = Payment(
            id=uuid4(),
            user_id=mock_user.id,
            plan_id="pkg-2",
            plan_name="Pro",
            credits_purchased=200,
            amount=Decimal("19.99"),
            currency="NGN",
            reference="REF-2",
            status=PaymentStatus.SUCCESS,
            payment_method=PaymentMethod.CARD,
            provider=PaymentProvider.NOMBA,
            created_at=now,
            completed_at=now,
        )
        mock_purchases = [payment1, payment2]

        mock_db = AsyncMock()

        # First call returns successful purchases
        mock_result1 = MagicMock()
        mock_result1.scalars.return_value.all.return_value = mock_purchases

        # Second call returns recent history
        mock_result2 = MagicMock()
        mock_result2.scalars.return_value.all.return_value = mock_purchases

        mock_db.execute = AsyncMock(side_effect=[mock_result1, mock_result2])

        mock_request = MagicMock()

        result = await get_credits_overview(
            request=mock_request,
            current_user=mock_user,
            db=mock_db,
        )

        assert result.current_balance == 250
        assert result.total_purchased == 300
        # Use pytest.approx for floating point comparison
        assert result.total_spent == pytest.approx(29.98, rel=1e-2)


class TestNombaWebhook:
    """Tests for nomba_webhook endpoint."""

    @pytest.mark.asyncio
    async def test_invalid_signature_rejected(self):
        """Test webhook rejects invalid signature."""
        from app.billing.routes import nomba_webhook

        mock_request = MagicMock()
        mock_request.body = AsyncMock(return_value=b'{"test": "data"}')
        mock_request.headers = {"X-Nomba-Signature": "invalid"}

        mock_db = AsyncMock()

        with patch("app.billing.routes.settings") as mock_settings:
            mock_settings.nomba_webhook_secret = "test-secret"

            with pytest.raises(HTTPException) as exc:
                await nomba_webhook(request=mock_request, db=mock_db)

            assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_skips_signature_when_secret_not_configured(self):
        """Test webhook skips signature verification when secret not configured."""
        from app.billing.routes import nomba_webhook

        mock_request = MagicMock()
        mock_request.body = AsyncMock(return_value=b'{}')
        mock_request.headers = {}
        mock_request.json = AsyncMock(return_value={})

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch("app.billing.routes.settings") as mock_settings:
            mock_settings.nomba_webhook_secret = ""  # Not configured

            with patch("app.billing.routes.nomba_provider") as mock_provider:
                mock_provider.handle_webhook = AsyncMock(
                    return_value={
                        "success": True,
                        "processed": True,
                        "order_reference": "REF-123",
                    }
                )

                result = await nomba_webhook(request=mock_request, db=mock_db)

                # Should not raise, just process
                assert result["status"] == "received"

    @pytest.mark.asyncio
    async def test_webhook_processes_successful_payment(self):
        """Test webhook processes successful payment."""
        from app.billing.routes import nomba_webhook

        payload = {
            "orderReference": "REF-123",
            "status": "success",
            "amount": "1000.00",
        }

        mock_request = MagicMock()
        mock_request.body = AsyncMock(return_value=b'{}')
        mock_request.headers = {}
        mock_request.json = AsyncMock(return_value=payload)

        mock_payment = MagicMock()
        mock_payment.status = PaymentStatus.PENDING
        mock_payment.credits_purchased = 100
        mock_payment.user_id = uuid4()

        mock_user = MagicMock()
        mock_user.credits = 0

        mock_db = AsyncMock()

        # First call returns payment
        mock_result1 = MagicMock()
        mock_result1.scalar_one_or_none.return_value = mock_payment

        # Second call returns user
        mock_result2 = MagicMock()
        mock_result2.scalar_one_or_none.return_value = mock_user

        mock_db.execute = AsyncMock(side_effect=[mock_result1, mock_result2])

        with patch("app.billing.routes.settings") as mock_settings:
            mock_settings.nomba_webhook_secret = ""

            with patch("app.billing.routes.nomba_provider") as mock_provider:
                mock_provider.handle_webhook = AsyncMock(
                    return_value={
                        "success": True,
                        "processed": True,
                        "order_reference": "REF-123",
                        "status": "success",
                        "payment_reference": "PAY-123",
                        "raw_payload": payload,
                    }
                )

                result = await nomba_webhook(request=mock_request, db=mock_db)

                assert result["status"] == "received"
                assert result["processed"] is True
                assert mock_user.credits == 100

    @pytest.mark.asyncio
    async def test_webhook_skips_already_processed(self):
        """Test webhook skips already processed payment."""
        from app.billing.routes import nomba_webhook

        mock_request = MagicMock()
        mock_request.body = AsyncMock(return_value=b'{}')
        mock_request.headers = {}
        mock_request.json = AsyncMock(
            return_value={"orderReference": "REF-123", "status": "success"}
        )

        mock_payment = MagicMock()
        mock_payment.status = PaymentStatus.SUCCESS  # Already processed

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_payment
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch("app.billing.routes.settings") as mock_settings:
            mock_settings.nomba_webhook_secret = ""

            with patch("app.billing.routes.nomba_provider") as mock_provider:
                mock_provider.handle_webhook = AsyncMock(
                    return_value={
                        "success": True,
                        "processed": True,
                        "order_reference": "REF-123",
                    }
                )

                result = await nomba_webhook(request=mock_request, db=mock_db)

                assert result["processed"] is False
                assert result.get("reason") == "already_processed"

    @pytest.mark.asyncio
    async def test_webhook_handles_failed_payment(self):
        """Test webhook handles failed payment status."""
        from app.billing.routes import nomba_webhook

        payload = {
            "orderReference": "REF-123",
            "status": "failed",
        }

        mock_request = MagicMock()
        mock_request.body = AsyncMock(return_value=b'{}')
        mock_request.headers = {}
        mock_request.json = AsyncMock(return_value=payload)

        mock_payment = MagicMock()
        mock_payment.status = PaymentStatus.PENDING

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_payment
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch("app.billing.routes.settings") as mock_settings:
            mock_settings.nomba_webhook_secret = ""

            with patch("app.billing.routes.nomba_provider") as mock_provider:
                mock_provider.handle_webhook = AsyncMock(
                    return_value={
                        "success": True,
                        "processed": True,
                        "order_reference": "REF-123",
                        "status": "failed",
                        "raw_payload": payload,
                    }
                )

                result = await nomba_webhook(request=mock_request, db=mock_db)

                assert result["status"] == "received"
                assert mock_payment.status == PaymentStatus.FAILED

    @pytest.mark.asyncio
    async def test_webhook_handles_exception(self):
        """Test webhook handles unexpected exception."""
        from app.billing.routes import nomba_webhook

        mock_request = MagicMock()
        mock_request.body = AsyncMock(return_value=b'{}')
        mock_request.headers = {}
        mock_request.json = AsyncMock(side_effect=Exception("Parse error"))

        mock_db = AsyncMock()

        with patch("app.billing.routes.settings") as mock_settings:
            mock_settings.nomba_webhook_secret = ""

            result = await nomba_webhook(request=mock_request, db=mock_db)

            assert result["status"] == "error"
            assert "Internal processing error" in result["message"]
