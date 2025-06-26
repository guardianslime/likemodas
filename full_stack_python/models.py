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
    
    # Relación con BlogPostModel
    posts: List['BlogPostModel'] = Relationship(
        back_populates='userinfo'
    )
    
    # CORRECCIÓN 1: Se actualiza el tipo a 'ContactEntryModel'
    # Relación con ContactEntryModel
    contact_entries: List['ContactEntryModel'] = Relationship(
        back_populates='userinfo'
    ) 
    
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
    # ¡CORRECCIÓN! Se hace obligatorio que un post tenga un autor.
    userinfo_id: int = Field(foreign_key="userinfo.id")
    userinfo: "UserInfo" = Relationship(back_populates="posts")
    
    title: str
    content: str
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
    publish_date: datetime = Field(
        default=None,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={},
        nullable=True
    )

class ContactEntryModel(rx.Model, table=True):
    # ¡CORRECCIÓN! Aseguramos larelación con 
    # el autor.
    userinfo_id: int = Field(foreign_key="userinfo.id")
    userinfo: "UserInfo" = Relationship(back_populates="contact_entries")
    
    title: str
    content: str
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
    publish_date: datetime = Field(
        default=None,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={},
        nullable=True
    )
