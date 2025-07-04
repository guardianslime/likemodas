# full_stack_python/models.py

from typing import Optional, List
from datetime import datetime
import reflex as rx
from reflex_local_auth.user import LocalUser
import sqlalchemy
from sqlmodel import Field, Relationship
from . import utils

# ... (Las clases UserInfo no cambian) ...

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
    image_filename: Optional[str] = None  # ¡NUEVO CAMPO!
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

def contact_entry_list_item(contact: ContactEntryModel) -> rx.Component:
    """Muestra una entrada de contacto individual."""
    return rx.box(
        rx.heading(f"{contact.first_name} ({contact.email})", size="4"),
        rx.text(contact.message, white_space="pre-wrap", margin_y="0.5em"),
        
        # --- SOLUCIÓN DEFINITIVA ---
        # Usamos .to_string() sin argumentos. Esto es compatible y evitará el error.
        rx.text(f"Recibido el: {contact.created_at.to_string()}", size="2", color_scheme="gray"),
        # ---------------------------

        rx.cond(
            contact.userinfo_id,
            rx.text("Enviado por un usuario registrado", size="2", weight="bold"),
            rx.text("Enviado por un invitado", size="2", weight="bold"),
        ),
        padding="1em", border="1px solid", border_color=rx.color("gray", 6), border_radius="0.5em", width="100%"
    )