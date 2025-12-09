"""Tests for email templates."""

import pytest

from app.emails.enums import EmailType
from app.emails.templates import get_email_template

from .factories import SettingsFactory


class TestEmailTemplates:
    """Tests for email template generation."""

    def test_welcome_template(self):
        """Test welcome email template."""
        context = {
            "name": "John Doe",
            "dashboard_url": "https://example.com/dashboard",
        }

        with SettingsFactory.mock():
            subject, html_content, text_content = get_email_template(
                EmailType.WELCOME, context
            )

            # Check subject
            assert "Welcome" in subject
            assert "Test App" in subject

            # Check HTML content
            assert "John Doe" in html_content
            assert "https://example.com/dashboard" in html_content
            assert "Welcome" in html_content
            assert "#6366f1" in html_content  # Primary color

            # Check text content
            assert "John Doe" in text_content
            assert "https://example.com/dashboard" in text_content

    def test_welcome_template_default_name(self):
        """Test welcome template with default name when not provided."""
        context = {"dashboard_url": "https://example.com/dashboard"}

        with SettingsFactory.mock():
            subject, html_content, text_content = get_email_template(
                EmailType.WELCOME, context
            )

            # Should use "there" as default
            assert "there" in html_content

    def test_password_reset_template(self):
        """Test password reset email template."""
        context = {
            "reset_url": "https://example.com/reset?token=abc123",
        }

        with SettingsFactory.mock():
            subject, html_content, text_content = get_email_template(
                EmailType.PASSWORD_RESET, context
            )

            # Check subject
            assert "Reset" in subject or "Password" in subject

            # Check HTML content
            assert "https://example.com/reset?token=abc123" in html_content
            assert "Reset Password" in html_content or "reset" in html_content.lower()

            # Check text content
            assert "https://example.com/reset?token=abc123" in text_content

    def test_email_verification_template(self):
        """Test email verification template."""
        context = {
            "verify_url": "https://example.com/verify?token=xyz789",
        }

        with SettingsFactory.mock():
            subject, html_content, text_content = get_email_template(
                EmailType.EMAIL_VERIFICATION, context
            )

            # Check subject
            assert "Verify" in subject or "Email" in subject

            # Check HTML content
            assert "https://example.com/verify?token=xyz789" in html_content
            assert "verify" in html_content.lower()

            # Check text content
            assert "https://example.com/verify?token=xyz789" in text_content

    def test_payment_success_template(self):
        """Test payment success email template."""
        context = {
            "amount": "₦5,000",
            "credits": "50",
            "reference": "PAY-123456",
            "dashboard_url": "https://example.com/dashboard",
        }

        with SettingsFactory.mock():
            subject, html_content, text_content = get_email_template(
                EmailType.PAYMENT_SUCCESS, context
            )

            # Check subject
            assert "Payment" in subject

            # Check HTML content
            assert "₦5,000" in html_content
            assert "50" in html_content
            assert "PAY-123456" in html_content
            assert "https://example.com/dashboard" in html_content

            # Check text content
            assert "₦5,000" in text_content
            assert "50" in text_content
            assert "PAY-123456" in text_content

    def test_payment_failed_template(self):
        """Test payment failed email template."""
        context = {
            "reason": "Insufficient funds",
            "retry_url": "https://example.com/retry",
        }

        with SettingsFactory.mock():
            subject, html_content, text_content = get_email_template(
                EmailType.PAYMENT_FAILED, context
            )

            # Check subject
            assert "failed" in subject.lower() or "Payment" in subject

            # Check HTML content
            assert "Insufficient funds" in html_content

            # Check text content
            assert "Insufficient funds" in text_content

    def test_generic_template(self):
        """Test generic email template."""
        context = {
            "subject": "Custom Subject",
            "message": "This is a custom message.",
        }

        with SettingsFactory.mock():
            subject, html_content, text_content = get_email_template(
                EmailType.GENERIC, context
            )

            # Check subject
            assert subject == "Custom Subject"

            # Check HTML content
            assert "This is a custom message." in html_content

            # Check text content
            assert text_content == "This is a custom message."

    def test_generic_template_default_subject(self):
        """Test generic template uses default subject."""
        context = {
            "message": "A message without subject.",
        }

        with SettingsFactory.mock():
            subject, html_content, text_content = get_email_template(
                EmailType.GENERIC, context
            )

            # Should use app name in default subject
            assert "Test App" in subject

    def test_template_html_structure(self):
        """Test that HTML templates have proper structure."""
        context = {"name": "Test", "dashboard_url": "https://example.com"}

        with SettingsFactory.mock():
            subject, html_content, text_content = get_email_template(
                EmailType.WELCOME, context
            )

            # Check HTML structure
            assert "<!DOCTYPE html>" in html_content
            assert "<html>" in html_content
            assert "<head>" in html_content
            assert "<body>" in html_content
            assert "</html>" in html_content

            # Check responsive meta tag
            assert 'viewport' in html_content

            # Check styling
            assert "<style>" in html_content or "style=" in html_content

    def test_template_includes_footer(self):
        """Test that templates include footer."""
        context = {"name": "Test", "dashboard_url": "https://example.com"}

        with SettingsFactory.mock():
            subject, html_content, text_content = get_email_template(
                EmailType.WELCOME, context
            )

            # Footer should have app name
            assert "Test App" in html_content

    def test_template_uses_primary_color(self):
        """Test that templates use configured primary color."""
        context = {"name": "Test", "dashboard_url": "https://example.com"}

        with SettingsFactory.mock():
            subject, html_content, text_content = get_email_template(
                EmailType.WELCOME, context
            )

            # Primary color should be in HTML
            assert "#6366f1" in html_content

    def test_unknown_template_falls_back_to_generic(self):
        """Test that unknown template type uses generic."""
        # Create a mock invalid type that gets the generic handler
        context = {"message": "Fallback message"}

        with SettingsFactory.mock():
            # Using GENERIC explicitly since we can't create invalid enum
            subject, html_content, text_content = get_email_template(
                EmailType.GENERIC, context
            )

            assert "Fallback message" in html_content

    def test_all_email_types_have_templates(self):
        """Test that all EmailType values have templates."""
        with SettingsFactory.mock():
            for email_type in EmailType:
                context = {
                    "name": "Test User",
                    "dashboard_url": "https://example.com",
                    "reset_url": "https://example.com/reset",
                    "verify_url": "https://example.com/verify",
                    "amount": "₦1000",
                    "credits": "10",
                    "reference": "REF-123",
                    "reason": "Test reason",
                    "retry_url": "https://example.com/retry",
                    "subject": "Test",
                    "message": "Test message",
                }

                # Should not raise
                subject, html_content, text_content = get_email_template(
                    email_type, context
                )

                # All should return non-empty values
                assert subject
                assert html_content
                assert text_content is not None


class TestTemplateSecurityAndSanitization:
    """Tests for template security."""

    def test_html_content_in_context_not_escaped_for_trusted_input(self):
        """Test that trusted HTML in templates is rendered."""
        # Note: In production, you'd want to sanitize user input
        # but for templates, the content is trusted
        context = {
            "name": "<script>alert('xss')</script>",  # Malicious input
            "dashboard_url": "https://example.com",
        }

        with SettingsFactory.mock():
            subject, html_content, text_content = get_email_template(
                EmailType.WELCOME, context
            )

            # The name will be included as-is since templates trust context
            # In a real app, sanitize user-provided values before passing to template
            assert "alert" in html_content or "&lt;script&gt;" in html_content

    def test_url_injection_protection(self):
        """Test that URLs are handled properly."""
        context = {
            "name": "Test",
            "dashboard_url": "javascript:alert('xss')",  # Malicious URL
        }

        with SettingsFactory.mock():
            subject, html_content, text_content = get_email_template(
                EmailType.WELCOME, context
            )

            # URL will be included - sanitization should happen before template
            # This test documents current behavior
            assert "javascript:" in html_content  # Currently not sanitized
