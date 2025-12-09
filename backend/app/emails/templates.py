"""Email templates."""

from app.core.config import settings
from app.emails.enums import EmailType


def get_email_template(email_type: EmailType, context: dict) -> tuple[str, str, str]:
    """
    Get email subject and content for a given type.

    Returns:
        Tuple of (subject, html_content, text_content)
    """
    templates = {
        EmailType.WELCOME: _welcome_template,
        EmailType.PASSWORD_RESET: _password_reset_template,
        EmailType.EMAIL_VERIFICATION: _email_verification_template,
        EmailType.PAYMENT_SUCCESS: _payment_success_template,
        EmailType.PAYMENT_FAILED: _payment_failed_template,
        EmailType.GENERIC: _generic_template,
    }

    template_fn = templates.get(email_type, _generic_template)
    return template_fn(context)


def _base_html(content: str, title: str = "") -> str:
    """Wrap content in base HTML template."""
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            padding: 20px 0;
            border-bottom: 1px solid #eee;
        }}
        .content {{
            padding: 30px 0;
        }}
        .button {{
            display: inline-block;
            padding: 12px 24px;
            background-color: {settings.primary_color};
            color: white;
            text-decoration: none;
            border-radius: 6px;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            padding: 20px 0;
            border-top: 1px solid #eee;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1 style="color: {settings.primary_color};">{settings.app_name}</h1>
    </div>
    <div class="content">
        {content}
    </div>
    <div class="footer">
        <p>&copy; {settings.app_name}. All rights reserved.</p>
    </div>
</body>
</html>
"""


def _welcome_template(context: dict) -> tuple[str, str, str]:
    """Welcome email template."""
    name = context.get("name", "there")
    subject = f"Welcome to {settings.app_name}!"

    html_content = _base_html(
        f"""
        <h2>Welcome, {name}!</h2>
        <p>Thank you for joining {settings.app_name}. We're excited to have you on board.</p>
        <p>Get started by exploring your dashboard and setting up your profile.</p>
        <a href="{context.get('dashboard_url', '#')}" class="button">Go to Dashboard</a>
        <p>If you have any questions, feel free to reach out to our support team.</p>
        """,
        subject,
    )

    text_content = f"""
Welcome, {name}!

Thank you for joining {settings.app_name}. We're excited to have you on board.

Get started by exploring your dashboard: {context.get('dashboard_url', '')}

If you have any questions, feel free to reach out to our support team.
"""

    return subject, html_content, text_content


def _password_reset_template(context: dict) -> tuple[str, str, str]:
    """Password reset email template."""
    subject = f"Reset your {settings.app_name} password"
    reset_url = context.get("reset_url", "#")

    html_content = _base_html(
        f"""
        <h2>Password Reset Request</h2>
        <p>We received a request to reset your password. Click the button below to create a new password:</p>
        <a href="{reset_url}" class="button">Reset Password</a>
        <p>This link will expire in 1 hour.</p>
        <p>If you didn't request this, you can safely ignore this email.</p>
        """,
        subject,
    )

    text_content = f"""
Password Reset Request

We received a request to reset your password. Visit the link below to create a new password:

{reset_url}

This link will expire in 1 hour.

If you didn't request this, you can safely ignore this email.
"""

    return subject, html_content, text_content


def _email_verification_template(context: dict) -> tuple[str, str, str]:
    """Email verification template."""
    subject = f"Verify your email for {settings.app_name}"
    verify_url = context.get("verify_url", "#")

    html_content = _base_html(
        f"""
        <h2>Verify Your Email</h2>
        <p>Please verify your email address by clicking the button below:</p>
        <a href="{verify_url}" class="button">Verify Email</a>
        <p>This link will expire in 24 hours.</p>
        """,
        subject,
    )

    text_content = f"""
Verify Your Email

Please verify your email address by visiting:

{verify_url}

This link will expire in 24 hours.
"""

    return subject, html_content, text_content


def _payment_success_template(context: dict) -> tuple[str, str, str]:
    """Payment success email template."""
    subject = f"Payment confirmed - {settings.app_name}"
    amount = context.get("amount", "")
    credits = context.get("credits", "")

    html_content = _base_html(
        f"""
        <h2>Payment Successful!</h2>
        <p>Thank you for your payment. Here are the details:</p>
        <ul>
            <li><strong>Amount:</strong> {amount}</li>
            <li><strong>Credits added:</strong> {credits}</li>
            <li><strong>Reference:</strong> {context.get('reference', '')}</li>
        </ul>
        <p>Your credits have been added to your account.</p>
        <a href="{context.get('dashboard_url', '#')}" class="button">View Dashboard</a>
        """,
        subject,
    )

    text_content = f"""
Payment Successful!

Thank you for your payment. Here are the details:

- Amount: {amount}
- Credits added: {credits}
- Reference: {context.get('reference', '')}

Your credits have been added to your account.
"""

    return subject, html_content, text_content


def _payment_failed_template(context: dict) -> tuple[str, str, str]:
    """Payment failed email template."""
    subject = f"Payment failed - {settings.app_name}"
    reason = context.get("reason", "Unknown error")

    html_content = _base_html(
        f"""
        <h2>Payment Failed</h2>
        <p>Unfortunately, your payment could not be processed.</p>
        <p><strong>Reason:</strong> {reason}</p>
        <p>Please try again or contact support if the issue persists.</p>
        <a href="{context.get('retry_url', '#')}" class="button">Try Again</a>
        """,
        subject,
    )

    text_content = f"""
Payment Failed

Unfortunately, your payment could not be processed.

Reason: {reason}

Please try again or contact support if the issue persists.
"""

    return subject, html_content, text_content


def _generic_template(context: dict) -> tuple[str, str, str]:
    """Generic email template."""
    subject = context.get("subject", f"Message from {settings.app_name}")
    message = context.get("message", "")

    html_content = _base_html(f"<p>{message}</p>", subject)
    text_content = message

    return subject, html_content, text_content
