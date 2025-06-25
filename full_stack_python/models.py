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
    user: LocalUser | None = Relationship()
    posts: List['BlogPostModel'] = Relationship(
        back_populates='userinfo'
    )
    contact_entries: List['ContactEntryModel'] = Relationship(
        back_populates='userinfo'
    ) 
    created_at: datetime = Field(
        default_factory=utils.timing.get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={
            "server_default": sqlalchemy.func.now()
        },
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=utils.timing.get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={
            "onupdate": sqlalchemy.func.now(),
            "server_default": sqlalchemy.func.now()
        },
        nullable=False
    )


class BlogPostModel(rx.Model, table=True):
    # ¡CORRECCIÓN! Se hace obligatorio que un post tenga un autor eliminando `default=None`.
    userinfo_id: int = Field(foreign_key="userinfo.id")
    # ¡CORRECCIÓN! La relación con el autor ya no es opcional.
    userinfo: "UserInfo" = Relationship(back_populates="posts")
    
    title: str
    content: str
    created_at: datetime = Field(
        default_factory=utils.timing.get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={
            "server_default": sqlalchemy.func.now()
        },
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=utils.timing.get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={
            "onupdate": sqlalchemy.func.now(),
            "server_default": sqlalchemy.func.now()
        },
        nullable=False
    )
    publish_active: bool = False
    publish_date: datetime = Field(
        default=None,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={},
        nullable=True
    )



class User(rx.Model, table=True):
    """User model."""
    id: Union[int, None] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str
    enabled: bool = True
    
    # Se usa List en lugar de list para compatibilidad
    contact_entries: List["ContactEntry"] = Relationship(back_populates="user")


# --- Modelo de Entrada de Contacto corregido y compatible ---
class ContactEntry(rx.Model, table=True):
    """Contact entry model."""
    id: Union[int, None] = Field(default=None, primary_key=True)
    name: str
    email: str
    message: str
    
    # Se usa Union en lugar de |
    user_id: Union[int, None] = Field(default=None, foreign_key="user.id")
    user: Union["User", None] = Relationship(back_populates="contact_entries")


# --- Modelo de Blog corregido y compatible ---
class Blog(rx.Model, table=True):
    """Blog model."""
    id: Union[int, None] = Field(default=None, primary_key=True)
    author: str
    title: str
    content: str
    created_at: str
    updated_at: str