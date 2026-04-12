"""Email templates using Jinja2."""

from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import settings
from app.emails.enums import EmailType

# Set up Jinja2 environment
TEMPLATES_DIR = Path(__file__).parent / "templates" / "app"

_jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)


def get_base_context() -> dict:
    """Get base context for all email templates."""
    return {
        "app_name": settings.app_name,
        "primary_color": settings.primary_color,
        "current_year": datetime.now().year,
        "logo_url": None,  # Can be set via settings if needed
    }


def render_email_template(template_name: str, context: dict) -> str:
    """
    Render an email template with the given context.

    Args:
        template_name: Name of the template file (e.g., 'welcome.html')
        context: Template context variables

    Returns:
        Rendered HTML string
    """
    template = _jinja_env.get_template(template_name)
    full_context = {**get_base_context(), **context}
    return template.render(**full_context)


def get_email_template(email_type: EmailType, context: dict) -> tuple[str, str, str]:
    """
    Get email subject and content for a given type.

    Args:
        email_type: Type of email to send
        context: Template context variables

    Returns:
        Tuple of (subject, html_content, text_content)
    """
    template_map = {
        EmailType.WELCOME: ("welcome.html", f"Welcome to {settings.app_name}!"),
        EmailType.PASSWORD_RESET: ("password_reset.html", f"Reset your {settings.app_name} password"),
        EmailType.EMAIL_VERIFICATION: ("email_verification.html", f"Verify your email for {settings.app_name}"),
        EmailType.PAYMENT_SUCCESS: ("payment_success.html", f"Payment confirmed - {settings.app_name}"),
        EmailType.PAYMENT_FAILED: ("payment_failed.html", f"Payment failed - {settings.app_name}"),
        EmailType.GENERIC: ("generic.html", context.get("subject", f"Message from {settings.app_name}")),
    }

    template_name, default_subject = template_map.get(
        email_type, ("generic.html", f"Message from {settings.app_name}")
    )
    subject = context.get("subject", default_subject)

    # Render HTML
    html_content = render_email_template(template_name, context)

    # Generate plain text version (simple strip of HTML)
    text_content = _generate_text_content(email_type, context)

    return subject, html_content, text_content


def _generate_text_content(email_type: EmailType, context: dict) -> str:
    """Generate plain text version of email."""
    app_name = settings.app_name

    if email_type == EmailType.WELCOME:
        name = context.get("name", "there")
        dashboard_url = context.get("dashboard_url", "")
        return f"""
Welcome, {name}!

Thanks for joining {app_name}. We're excited to have you on board.

Get started by visiting your dashboard: {dashboard_url}

If you have any questions, feel free to reach out to our support team.

- The {app_name} Team
"""

    elif email_type == EmailType.PASSWORD_RESET:
        reset_url = context.get("reset_url", "")
        return f"""
Password Reset Request

We received a request to reset your password for your {app_name} account.

Reset your password: {reset_url}

This link will expire in 1 hour.

If you didn't request this, you can safely ignore this email.

- The {app_name} Team
"""

    elif email_type == EmailType.EMAIL_VERIFICATION:
        verify_url = context.get("verify_url", "")
        return f"""
Verify Your Email

Please verify your email address for {app_name}.

Verify: {verify_url}

This link will expire in 24 hours.

- The {app_name} Team
"""

    elif email_type == EmailType.PAYMENT_SUCCESS:
        amount = context.get("amount", "")
        credits = context.get("credits", "")
        reference = context.get("reference", "")
        return f"""
Payment Successful!

Thank you for your payment. Here are the details:

- Amount: {amount}
- Credits added: {credits}
- Reference: {reference}

Your credits have been added to your account.

- The {app_name} Team
"""

    elif email_type == EmailType.PAYMENT_FAILED:
        reason = context.get("reason", "Unknown error")
        return f"""
Payment Failed

Unfortunately, your payment could not be processed.

Reason: {reason}

Please try again or contact support if the issue persists.

- The {app_name} Team
"""

    else:
        message = context.get("message", "")
        return f"""
{message}

- The {app_name} Team
"""
