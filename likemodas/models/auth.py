from sqlmodel import Field, Relationship
from typing import Optional
from datetime import datetime
import reflex as rx

# Importación directa para que esté disponible en tiempo de ejecución.
# Esto es clave para que Reflex encuentre el tipo 'UserInfo'.
from .user import UserInfo


class VerificationToken(rx.Model, table=True):
    token: str = Field(unique=True, index=True)
    userinfo_id: int = Field(foreign_key="userinfo.id")
    expires_at: datetime
    
    # Se usa el tipo real 'UserInfo' en lugar de un string "UserInfo".
    # Esto ayuda a Reflex a entender la relación directamente.
    userinfo: UserInfo = Relationship(back_populates="verification_tokens")


class PasswordResetToken(rx.Model, table=True):
    token: str = Field(unique=True, index=True)
    user_id: int = Field(foreign_key="localuser.id")
    expires_at: datetime


class LocalUser(rx.Model, table=True):
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    password_hash: bytes
    
    # Aquí también usamos el tipo real para la relación.
    userinfo: Optional["UserInfo"] = Relationship(back_populates="user")
