# likemodas/blog/list.py

import reflex as rx
from ..auth.admin_auth import require_admin
from ..ui.base import base_page
from ..models import BlogPostModel
from .. import navigation
from .state import BlogPostState

def _gallery_card(post: BlogPostModel) -> rx.Component:
    return rx.link(
        rx.card(
            rx.inset(
                rx.cond(
                    post.image_urls,
                    rx.image(
                        src=rx.get_upload_url(post.image_urls[0]),
                        width="100%",
                        height="140px",
                        object_fit="cover",
                    ),
                    rx.box(
                        rx.icon("image_off", size=48),
                        height="140px",
                        width="100%",
                        bg=rx.color("gray", 4),
                        display="flex",
                        align_items="center",
                        justify_content="center",
                    )
                )
            ),
            rx.text(post.title, weight="bold", as_="div", size="3", margin_bottom="1"),
            rx.text(post.content, as_="p", size="2", color_scheme="gray", trim="end", height="4.5em"),
        ),
        href=f"/blog-public/{post.id}",
        as_child=True,
        style={"text_decoration": "none"}
    )

@require_admin
def blog_post_list_page() -> rx.Component:
    """Página que muestra la galería de posts del admin."""
    return base_page(
        rx.center(
            rx.vstack(
                rx.heading("Mis Publicaciones", size="8", margin_bottom="1em"),
                
                rx.input(
                    placeholder="Buscar por nombre...",
                    value=BlogPostState.search_query,
                    on_change=BlogPostState.set_search_query,
                    width="100%",
                    max_width="400px",
                    margin_bottom="1.5em",
                ),

                rx.cond(
                    BlogPostState.filtered_posts,
                    rx.grid(
                        rx.foreach(BlogPostState.filtered_posts, _gallery_card),
                        columns="4", # Se fija a 4 columnas
                        spacing="6",
                        width="100%",
                        max_width="1200px",
                    ),
                    rx.center(rx.text("No se encontraron publicaciones."), padding_y="4em")
                ),
                spacing="6",
                width="100%",
                padding="2em",
                align="center"
            ),
            width="100%"
        )
    )