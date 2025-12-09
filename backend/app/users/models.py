"""User models using SQLAlchemy 2.0."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
import uuid

import bcrypt
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base.models import BaseModel

if TYPE_CHECKING:
    from app.payments.models import Payment


class User(BaseModel):
    """User model."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255))

    # Supabase integration
    supabase_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    # Credits/balance for payments
    credits: Mapped[int] = mapped_column(Integer, default=0)
    last_purchase_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Metadata
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False)

    # User Preferences
    email_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    marketing_emails: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    profile: Mapped[Optional["UserProfile"]] = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    payments: Mapped[list["Payment"]] = relationship(
        "Payment",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __str__(self) -> str:
        return f"{self.full_name} ({self.email})"

    def set_password(self, plain_password: str) -> None:
        """Hash and set the user's password."""
        hashed = bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt())
        self.password = hashed.decode()

    def check_password(self, plain_password: str) -> bool:
        """Verify a plain text password against the hashed password."""
        if not self.password:
            return False
        return bcrypt.checkpw(plain_password.encode(), self.password.encode())


class UserProfile(BaseModel):
    """User profile model with extended information."""

    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
    )

    # Profile Information
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    avatar_version: Mapped[int] = mapped_column(Integer, default=1)
    website_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    github_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Professional Information
    current_position: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    company: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Preferences
    theme: Mapped[str] = mapped_column(String(50), default="system")

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="profile")
