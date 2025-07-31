from sqlmodel import Field, Relationship
from typing import Optional
from datetime import datetime
import reflex as rx

# --- CAMBIO CLAVE ---
# Se importa 'UserInfo' directamente, fuera del bloque TYPE_CHECKING.
# Esto asegura que el compilador de Reflex pueda encontrar y resolver el tipo
# 'UserInfo' cuando lo necesite para la relación en NotificationModel.
from .user import UserInfo

from .base import format_utc_to_local

class NotificationModel(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    userinfo_id: int = Field(foreign_key="userinfo.id")
    message: str
    is_read: bool = Field(default=False)
    url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # La relación se mantiene como un string ("forward reference").
    # El import que añadimos arriba permite que esto se resuelva correctamente.
    userinfo: "UserInfo" = Relationship(back_populates="notifications")

    @property
    def created_at_formatted(self) -> str:
        return format_utc_to_local(self.created_at)


class ContactEntryModel(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    userinfo_id: Optional[int] = Field(default=None, foreign_key="userinfo.id")
    first_name: str
    last_name: Optional[str] = None
    email: Optional[str] = None
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    userinfo: Optional["UserInfo"] = Relationship(back_populates="contact_entries")

    @property
    def created_at_formatted(self) -> str:
        return format_utc_to_local(self.created_at)
