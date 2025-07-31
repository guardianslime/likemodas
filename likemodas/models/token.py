# -----------------------------------------------------------------------------
# likemodas/models/token.py (ARCHIVO CORREGIDO)
# -----------------------------------------------------------------------------
from sqlmodel import Field, Relationship
from typing import Optional
from datetime import datetime
import reflex as rx

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .user import UserInfo

class VerificationToken(rx.Model, table=True):
    # ✅ SOLUCIÓN: Se añade __table_args__ para permitir la redefinición del modelo.
    # Esto soluciona el error "Table 'verificationtoken' is already defined".
    __table_args__ = {"extend_existing": True}
    
    token: str = Field(unique=True, index=True)
    userinfo_id: int = Field(foreign_key="userinfo.id")
    expires_at: datetime
    
    userinfo: "UserInfo" = Relationship(back_populates="verification_tokens")

class PasswordResetToken(rx.Model, table=True):
    # ✅ SOLUCIÓN: Se añade por consistencia y para prevenir errores futuros.
    __table_args__ = {"extend_existing": True}

    token: str = Field(unique=True, index=True)
    user_id: int = Field(foreign_key="localuser.id")
    expires_at: datetime