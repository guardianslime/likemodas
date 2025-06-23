# -----------------------------------------------------------------
# full_stack_python/models.py (VERSIÓN CORREGIDA)
# -----------------------------------------------------------------
from typing import Optional, List
from datetime import datetime
import reflex as rx
from reflex_local_auth.user import LocalUser

import sqlalchemy
from sqlmodel import Field, Relationship

# Asumimos que tienes un archivo utils/timing.py, si no es así, puedes
# reemplazar utils.timing.get_utc_now con datetime.utcnow
from . import utils

class UserInfo(rx.Model, table=True):
    """
    Información extendida del usuario.
    Esta tabla se vincula al usuario de autenticación base.
    """
    email: str
    user_id: int = Field(unique=True, foreign_key='localuser.id')
    user: Optional[LocalUser] = Relationship()
    
    # Relaciones con otras tablas
    posts: List["BlogPostModel"] = Relationship(back_populates="userinfo")
    contact_entries: List["ContactEntryModel"] = Relationship(back_populates="userinfo")
    
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
    """Modelo para las publicaciones del blog."""
    title: str
    content: str
    
    # Un post siempre debe tener un autor.
    userinfo_id: int = Field(foreign_key="userinfo.id")
    userinfo: UserInfo = Relationship(back_populates="posts")
    
    publish_active: bool = False
    publish_date: Optional[datetime] = Field(
        default=None,
        sa_type=sqlalchemy.DateTime(timezone=True),
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

class ContactEntryModel(rx.Model, table=True):
    """Modelo para las entradas del formulario de contacto."""
    first_name: str
    message: str
    last_name: Optional[str] = None
    email: Optional[str] = None
    
    # Una entrada de contacto puede ser de un visitante (anónimo)
    # o de un usuario registrado. Por eso la relación es opcional.
    userinfo_id: Optional[int] = Field(default=None, foreign_key="userinfo.id")
    userinfo: Optional["UserInfo"] = Relationship(back_populates="contact_entries")
    
    created_at: datetime = Field(
        default_factory=utils.timing.get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={"server_default": sqlalchemy.func.now()},
        nullable=False
    )