# full_stack_python/models.py (CORREGIDO)

from typing import Optional, List
from datetime import datetime
import reflex as rx
from reflex_local_auth.user import LocalUser
import sqlalchemy
from sqlmodel import Field, Relationship
from . import utils

# ... (Clase UserInfo sin cambios) ...
class UserInfo(rx.Model, table=True):
    email: str
    user_id: int = Field(foreign_key="localuser.id")
    user: Optional[LocalUser] = Relationship()
    posts: List["BlogPostModel"] = Relationship(back_populates="userinfo")
    contact_entries: List["ContactEntryModel"] = Relationship(
        back_populates="userinfo"
    )
    created_at: datetime = Field(
        default_factory=utils.timing.get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={"server_default": sqlalchemy.func.now()},
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=utils.timing.get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={"onupdate": sqlalchemy.func.now(), "server_default": sqlalchemy.func.now()},
        nullable=False,
    )


class BlogPostModel(rx.Model, table=True):
    userinfo_id: int = Field(foreign_key="userinfo.id")
    userinfo: "UserInfo" = Relationship(back_populates="posts")
    title: str
    content: str
    price: float = 0.0
    images: list[str] = Field(default=[], sa_column=Column(JSON))
    publish_active: bool = False
    publish_date: datetime = Field(default_factory=datetime.utcnow)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def created_at_formatted(self) -> str:
        return self.created_at.strftime("%Y-%m-%d")

    @property
    def publish_date_formatted(self) -> str:
        if not self.publish_date:
            return ""
        return self.publish_date.strftime("%d-%m-%Y")

# ... (Clase ContactEntryModel sin cambios) ...
class ContactEntryModel(rx.Model, table=True):
    userinfo_id: Optional[int] = Field(default=None, foreign_key="userinfo.id")
    userinfo: Optional["UserInfo"] = Relationship(back_populates="contact_entries")
    first_name: str
    last_name: Optional[str] = None
    email: Optional[str] = None
    message: str
    created_at: datetime = Field(
        default_factory=utils.timing.get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={"server_default": sqlalchemy.func.now()},
        nullable=False,
    )

    @property
    def created_at_formatted(self) -> str:
        """Devuelve la fecha de creación como string formateado."""
        return self.created_at.strftime("%Y-%m-%d %H:%M")

    def dict(self, **kwargs):
        return super().dict(**kwargs) | {"created_at_formatted": self.created_at_formatted}