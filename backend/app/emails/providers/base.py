"""Base email provider interface."""

from abc import ABC, abstractmethod

from app.emails.enums import EmailProvider
from app.emails.schemas import EmailRequest, EmailResponse


class BaseEmailProvider(ABC):
    """Abstract base class for email providers."""

    provider: EmailProvider

    @staticmethod
    @abstractmethod
    async def send(
        request: EmailRequest,
        attachment_content: bytes | None = None,
        attachment_filename: str | None = None,
    ) -> EmailResponse:
        """Send an email."""
        pass

    @staticmethod
    @abstractmethod
    async def health_check() -> bool:
        """Check if the provider is configured and reachable."""
        pass
