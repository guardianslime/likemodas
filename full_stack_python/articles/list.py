# full_stack_python/articles/list.py

import reflex as rx
from .. import navigation
from ..ui.base import base_page
from ..models import BlogPostModel
from . import state

def article_card_link(post: BlogPostModel) -> rx.Component:
    """Componente de tarjeta para un artículo, ahora con imagen."""
    post_detail_url = f"{navigation.routes.ARTICLE_LIST_ROUTE}/{post.id}"
    return rx.card(
        rx.link(
            rx.flex(
                # --- CORRECCIÓN: Se añade la imagen a la tarjeta ---
                rx.cond(
                    post.image_url,
                    rx.image(
                        src=post.image_url,
                        width="8em",
                        height="8em",
                        object_fit="cover",
                        border_radius="0.5rem"
                    ),
                ),
                rx.box(
                    rx.heading(post.title, size="4"),
                    rx.cond(
                        post.userinfo,
                        rx.text(f"Autor: {post.userinfo.email}", size="2", color_scheme="gray")
                    )
                ),
                spacing="4",
                align_items="center",
            ),
            href=post_detail_url
        ),
        as_child=True
    )
    
# ... (el resto del archivo no necesita cambios)