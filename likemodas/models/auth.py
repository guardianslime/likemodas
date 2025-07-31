# -----------------------------------------------------------------------------
# likemodas/models/auth.py (ARCHIVO CORREGIDO)
# -----------------------------------------------------------------------------
from sqlmodel import Field, Relationship
from typing import Optional
from datetime import datetime
import reflex as rx

# ✅ SOLUCIÓN: Se usa TYPE_CHECKING para la importación del tipo.
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .user import UserInfo

class VerificationToken(rx.Model, table=True):
    token: str = Field(unique=True, index=True)
    userinfo_id: int = Field(foreign_key="userinfo.id")
    expires_at: datetime
    
    # Se usa un string para la relación.
    userinfo: "UserInfo" = Relationship(back_populates="verification_tokens")

class PasswordResetToken(rx.Model, table=True):
    token: str = Field(unique=True, index=True)
    user_id: int = Field(foreign_key="localuser.id")
    expires_at: datetime

class LocalUser(rx.Model, table=True):
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    password_hash: bytes
    
    # Se usa un string para la relación.
    userinfo: Optional["UserInfo"] = Relationship(back_populates="user")
