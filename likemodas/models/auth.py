from sqlmodel import Field, Relationship
from typing import Optional
from datetime import datetime
import reflex as rx

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import UserInfo

class VerificationToken(rx.Model, table=True):
    token: str = Field(unique=True, index=True)
    userinfo_id: int = Field(foreign_key="userinfo.id")
    expires_at: datetime
    userinfo: "UserInfo" = Relationship(back_populates="verification_tokens")

class PasswordResetToken(rx.Model, table=True):
    token: str = Field(unique=True, index=True)
    user_id: int = Field(foreign_key="localuser.id")
    expires_at: datetime

class LocalUser(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    password_hash: bytes
    userinfo: Optional["UserInfo"] = Relationship(back_populates="user")
