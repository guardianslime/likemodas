# full_stack_python/models.py

from typing import Optional, List
from datetime import datetime
import reflex as rx
from reflex_local_auth.user import LocalUser
import sqlalchemy
from sqlmodel import Field, Relationship
from . import utils

class UserInfo(rx.Model, table=True):
    email: str
    user_id: int = Field(foreign_key='localuser.id')
    user: Optional[LocalUser] = Relationship()
    posts: List['BlogPostModel'] = Relationship(back_populates='userinfo')
    contact_entries: List['ContactEntryModel'] = Relationship(back_populates='userinfo') 
    created_at: datetime = Field(
        default_factory=utils.timing.get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={"server_default": sqlalchemy.func.now()},
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=utils.timing.get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={"onupdate": sqlalchemy.func.now(), "server_default": sqlalchemy.func.now()},
        nullable=False
    )

class BlogPostModel(rx.Model, table=True):
    userinfo_id: int = Field(foreign_key="userinfo.id")
    userinfo: "UserInfo" = Relationship(back_populates="posts")
    title: str
    content: str
    image_url: Optional[str] = Field(default=None)
    created_at: datetime = Field(
        default_factory=utils.timing.get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={"server_default": sqlalchemy.func.now()},
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=utils.timing.get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={"onupdate": sqlalchemy.func.now(), "server_default": sqlalchemy.func.now()},
        nullable=False
    )
    publish_active: bool = False
    publish_date: Optional[datetime] = Field(
        default=None,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={},
        nullable=True
    )

class ContactEntryModel(rx.Model, table=True):
    userinfo_id: Optional[int] = Field(default=None, foreign_key="userinfo.id")
    userinfo: Optional['UserInfo'] = Relationship(back_populates="contact_entries")
    
    first_name: str
    last_name: Optional[str] = None
    email: Optional[str] = None
    message: str
    created_at: datetime = Field(
        default_factory=utils.timing.get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={"server_default": sqlalchemy.func.now()},
        nullable=False
    )

    # --- MÉTODO AÑADIDO Y CORREGIDO ---
    @rx.var
    def created_at_formatted(self) -> str:
        """Devuelve la fecha de creación formateada como un string."""
        return self.created_at.strftime("%Y-%m-%d %H:%M")