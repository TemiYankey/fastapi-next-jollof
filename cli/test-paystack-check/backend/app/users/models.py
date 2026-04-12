"""User models."""

import bcrypt
from tortoise import fields
from tortoise.fields.relational import OneToOneRelation, ReverseRelation

from app.base.models import BaseModel


class User(BaseModel):
    """User model."""

    email = fields.CharField(max_length=255, unique=True)
    password = fields.CharField(max_length=255, null=True)
    full_name = fields.CharField(max_length=255)

    # Supabase integration
    supabase_id = fields.CharField(max_length=255, unique=True)

    # Credits/balance for payments
    credits = fields.IntField(default=0)
    last_purchase_date = fields.DatetimeField(null=True)

    # Metadata
    last_login = fields.DatetimeField(null=True)
    is_active = fields.BooleanField(default=True)
    deleted_at = fields.DatetimeField(null=True)
    is_admin = fields.BooleanField(default=False)
    is_staff = fields.BooleanField(default=False)

    # User Preferences
    email_notifications = fields.BooleanField(default=True)
    marketing_emails = fields.BooleanField(default=False)

    profile: OneToOneRelation["UserProfile"]
    payments: ReverseRelation["Payment"]

    class Meta:
        table = "users"

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

    user: fields.OneToOneRelation["User"] = fields.OneToOneField(
        "users.User", related_name="profile"
    )

    # Profile Information
    bio = fields.TextField(null=True)
    phone = fields.CharField(max_length=50, null=True)
    location = fields.CharField(max_length=255, null=True)
    avatar_url = fields.CharField(max_length=255, null=True)
    avatar_version = fields.IntField(default=1)
    website_url = fields.CharField(max_length=500, null=True)
    linkedin_url = fields.CharField(max_length=500, null=True)
    github_url = fields.CharField(max_length=500, null=True)

    # Professional Information
    current_position = fields.CharField(max_length=255, null=True)
    company = fields.CharField(max_length=255, null=True)

    # Preferences
    theme = fields.CharField(max_length=50, default="system")

    class Meta:
        table = "user_profiles"
