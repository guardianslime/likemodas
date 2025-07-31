from sqlmodel import Field, Relationship
from typing import Optional
from datetime import datetime
import reflex as rx

import likemodas
from likemodas.models.user import UserInfo

# --- CAMBIO CLAVE 1 ---
# Se elimina la importación directa de 'UserInfo' para romper el ciclo de importación.

class VerificationToken(rx.Model, table=True):
    token: str = Field(unique=True, index=True)
    userinfo_id: int = Field(foreign_key="userinfo.id")
    expires_at: datetime
    
    # Se usa una referencia de string "UserInfo"
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
    
    # La relación ahora apunta a la ruta completa y sin ambigüedades de UserInfo.
    userinfo: Optional["likemodas.models.user.UserInfo"] = Relationship(back_populates="user")
