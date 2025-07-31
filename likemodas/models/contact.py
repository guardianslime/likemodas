# likemodas/models/contact.py

from sqlmodel import Field, Relationship
from typing import Optional
from datetime import datetime
import reflex as rx

# Corrección para evitar dependencias circulares
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .user import UserInfo

from .base import format_utc_to_local

class NotificationModel(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    userinfo_id: int = Field(foreign_key="userinfo.id")
    message: str
    is_read: bool = Field(default=False)
    url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Se usa un string ("UserInfo") para la referencia, que se resuelve de forma segura
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