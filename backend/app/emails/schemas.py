"""Email schemas."""

from pydantic import BaseModel, EmailStr

from app.emails.enums import EmailProvider, EmailType


class EmailRequest(BaseModel):
    """Email send request."""

    to: EmailStr
    subject: str
    html_content: str
    text_content: str | None = None
    from_email: str | None = None  # Override default sender
    from_name: str | None = None
    reply_to: EmailStr | None = None


class TemplatedEmailRequest(BaseModel):
    """Templated email request."""

    to: EmailStr
    email_type: EmailType
    context: dict = {}  # Template variables
    from_email: str | None = None
    from_name: str | None = None
    reply_to: EmailStr | None = None


class EmailResponse(BaseModel):
    """Email send response."""

    success: bool
    message_id: str | None = None
    provider: EmailProvider
    error: str | None = None


class EmailProviderConfig(BaseModel):
    """Email provider configuration."""

    provider: EmailProvider
    api_key: str
    from_email: str
    from_name: str | None = None
