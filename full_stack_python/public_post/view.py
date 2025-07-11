import reflex as rx
from full_stack_python.public_post.state import BlogViewState
from full_stack_python.ui.base import base_layout_component

# full_stack_python/models.py (CORREGIDO)

from full_stack_python.utils.timing import get_utc_now
from full_stack_python.models import UserInfo, BlogPostModel
from full_stack_python.models import ContactEntryModel
from typing import Optional, List
from sqlmodel import Field, Relationship
from sqlalchemy import Column, JSON
from datetime import datetime
import reflex as rx
from reflex_local_auth.user import LocalUser
import sqlalchemy
from sqlmodel import Field, Relationship


# ... (Clase ContactEntryModel sin cambios) ...
def public_post_detail_page() -> rx.Component:
    return base_layout_component(
        rx.box(
            rx.cond(
                BlogViewState.has_post,
                rx.flex(
                    _image_section(width="100%", height="400px"),
                    _info_section(width="100%"),
                    direction=rx.breakpoints("column", "column", "row"),
                    spacing="6",
                    width="100%",
                    max_width="1440px",
                    align_items="start",
                    wrap="wrap"
                ),
                rx.center(
                    rx.text("Publicación no encontrada.", color="red")
                )
            ),
            padding="2em",
            width="100%",
            max_width="1440px",
            margin="0 auto"
        ),
        on_mount=BlogViewState.on_load
    )

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
