import reflex as rx
from full_stack_python.public_post.state import BlogViewState
from full_stack_python.ui.base import base_layout_component

# full_stack_python/models.py (CORREGIDO)

from typing import Optional, List
from sqlmodel import Field, Relationship
from sqlalchemy import Column, JSON
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


def _image_section(width: str = "100%", height: str = "400px"):
    return rx.box(
        rx.box(
            rx.image(
                src=rx.cond(
                    BlogViewState.imagen_actual != "",
                    rx.get_upload_url(BlogViewState.imagen_actual),
                    "/no_image.png"
                ),
                width="100%",
                height="100%",
                object_fit="contain",
                border_radius="md"
            ),
            width="100%",
            height="100%",
            position="relative"
        ),
        rx.icon(
            tag="arrow_big_left",
            position="absolute",
            left="0.5em",
            top="50%",
            transform="translateY(-50%)",
            on_click=BlogViewState.anterior_imagen,
            cursor="pointer",
            box_size="2em"
        ),
        rx.icon(
            tag="arrow_big_right",
            position="absolute",
            right="0.5em",
            top="50%",
            transform="translateY(-50%)",
            on_click=BlogViewState.siguiente_imagen,
            cursor="pointer",
            box_size="2em"
        ),
        width=width,
        max_width="600px",
        height=height,
        position="relative",
        border_radius="md",
        overflow="hidden",
    )


def _info_section(width: str = "100%"):
    return rx.box(
        rx.vstack(
            rx.text(
                BlogViewState.post.title,
                size="6",
                font_weight="bold",
                margin_bottom="0.5em"
            ),
            rx.text(
                BlogViewState.formatted_price,
                size="5",
                color="gray"
            ),
            rx.text(
                BlogViewState.content,
                size="4",
                margin_top="1em",
                white_space="pre-wrap"
            )
        ),
        width=width,
        padding="2em"
    )
