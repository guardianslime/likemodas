import reflex as rx
import reflex_local_auth
from ..ui.base import base_page
from ..models import BlogPostModel
from .. import navigation
from .state import BlogPostState

def _gallery_card(post: BlogPostModel):
    """
    Una tarjeta de la galería para la sección de administración del blog.
    Visualmente idéntica a la de la sección pública, pero enlaza a /blog/[id].
    """
    return rx.box(
        rx.link(
            rx.vstack(
                rx.box(
                    rx.cond(
                        post.images & (post.images.length() > 0),
                        rx.image(
                            src=rx.get_upload_url(post.images[0]),
                            width="100%",
                            height="260px",
                            object_fit="cover",
                            border_radius="md",
                            style={"_hover": {"transform": "scale(1.05)"}}
                        ),
                        rx.box(
                            "Sin imagen",
                            width="100%",
                            height="260px",
                            bg="#eee",
                            align="center",
                            justify="center",
                            display="flex",
                            border_radius="md"
                        )
                    ),
                    position="relative",
                    width="100%",
                ),
                rx.text(
                    post.title,
                    weight="bold",
                    size="5",
                    color=rx.color_mode_cond("black", "white"),
                    as_="h3",
                    mt="0.5em"
                ),
                rx.text(
                    rx.cond(post.price, "$" + post.price.to(str), "$0.00"),
                    color=rx.color_mode_cond("black", "white"),
                    size="4",
                ),
                spacing="2",
                align="start",
                p="0.5em"
            ),
            # El enlace ahora apunta a la ruta de detalle DENTRO de la sección de blog
            href=f"{navigation.routes.BLOG_POSTS_ROUTE}/{post.id}"
        ),
        bg=rx.color_mode_cond("#f9f9f9", "#1D1D1D"),
        border=rx.color_mode_cond("1px solid #e5e5e5", "1px solid #2a2a2a"),
        border_radius="lg",
        box_shadow="lg",
        overflow="hidden",
        transition="all 0.2s ease-in-out",
    )

@reflex_local_auth.require_login
def blog_post_list_page() -> rx.Component:
    """Página que muestra la galería de posts del usuario logueado."""
    return base_page(
        rx.center(
            rx.vstack(
                rx.heading("Mis Publicaciones", size="8", margin_bottom="1em"),
                rx.cond(
                    BlogPostState.posts,
                    rx.grid(
                        rx.foreach(
                            BlogPostState.posts,
                            _gallery_card
                        ),
                        columns={"base": "1", "sm": "2", "md": "3", "lg": "4"},
                        spacing="6",
                        width="100%",
                        max_width="1200px",
                    ),
                    rx.center(rx.text("Aún no has escrito ningún post."), padding_y="4em")
                ),
                spacing="6",
                width="100%",
                padding="2em",
                align="center"
            ),
            width="100%"
        )
    )
