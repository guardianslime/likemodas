# full_stack_python/blog/public.py

import reflex as rx
from ..ui.base import base_page
from ..models import BlogPostModel
from ..navigation import routes
from .state import BlogPublicState

def public_blog_card(post: BlogPostModel) -> rx.Component:
    """Tarjeta para mostrar en la lista pública de blogs."""
    return rx.link(
        rx.card(
            rx.vstack(
                rx.image(
                    src=rx.get_upload_url(post.cover_image),
                    width="100%",
                    height="14em",
                    object_fit="cover",
                ),
                rx.vstack(
                    rx.heading(post.title, size="4"),
                    rx.text(
                        f"por {post.userinfo.email}",
                        size="2",
                        color_scheme="gray",
                    ),
                    align="start",
                    spacing="1",
                    padding="0.5em",
                ),
                spacing="2",
                height="100%"
            )
        ),
        href=f"{routes.BLOG_POSTS_ROUTE}/{post.id}", # Reutilizamos la página de detalle
        width="100%"
    )

def blog_public_page() -> rx.Component:
    """Página que muestra todas las publicaciones de todos los usuarios."""
    return base_page(
        rx.vstack(
            rx.heading("Blog de la Comunidad", size="9", text_align="center"),
            rx.text("Descubre las publicaciones de todos nuestros usuarios.", text_align="center"),
            rx.grid(
                rx.foreach(BlogPublicState.posts, public_blog_card),
                columns=["1", "2", "3", "4"],
                spacing="4",
                width="100%",
                margin_top="2em"
            ),
            spacing="5",
            width="100%",
            max_width="1400px",
            margin="auto",
            padding="1em",
            min_height="85vh"
        )
    )