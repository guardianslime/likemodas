# full_stack_python/models.py

from typing import Optional, List
from datetime import datetime
import reflex as rx
from reflex_local_auth.user import LocalUser
import sqlalchemy
from sqlmodel import Field, Relationship, select
from . import utils

# --- NUEVO MODELO PARA LAS IMÁGENES DEL BLOG ---
class PostImageModel(rx.Model, table=True):
    img_name: str
    post_id: int = Field(foreign_key="blogpostmodel.id")
    post: "BlogPostModel" = Relationship(back_populates="images")
    created_at: datetime = Field(
        default_factory=utils.timing.get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={"server_default": sqlalchemy.func.now()},
        nullable=False
    )

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
    
    # --- RELACIÓN CON IMÁGENES ---
    images: List[PostImageModel] = Relationship(
        back_populates="post",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"} # Para borrar en cascada
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
    publish_active: bool = False
    publish_date: Optional[datetime] = Field(
        default=None,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={},
        nullable=True
    )
    
    # --- PROPIEDAD CALCULADA PARA LA IMAGEN DE PORTADA ---
    @rx.var
    def cover_image(self) -> str:
        """Devuelve la primera imagen o una por defecto si no hay."""
        if self.images:
            return self.images[0].img_name
        return "/image_placeholder.svg" # Asegúrate de tener esta imagen en /assets

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

    @rx.var
    def created_at_formatted(self) -> str:
        """Un campo calculado que devuelve la fecha de creación como un string formateado."""
        return self.created_at.strftime("%Y-%m-%d %H:%M")