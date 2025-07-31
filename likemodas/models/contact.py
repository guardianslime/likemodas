from sqlmodel import Field, Relationship
from typing import Optional
from datetime import datetime
import reflex as rx

from likemodas.models.user import UserInfo
from .base import format_utc_to_local

class NotificationModel(rx.Model, table=True):
    userinfo_id: int = Field(foreign_key="userinfo.id")
    message: str
    is_read: bool = Field(default=False)
    url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    userinfo: "UserInfo" = Relationship(back_populates="notifications")

class ContactEntryModel(rx.Model, table=True):
    userinfo_id: Optional[int] = Field(default=None, foreign_key="userinfo.id")
    first_name: str
    last_name: Optional[str] = None
    email: Optional[str] = None
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    userinfo: Optional["UserInfo"] = Relationship(back_populates="contact_entries")
