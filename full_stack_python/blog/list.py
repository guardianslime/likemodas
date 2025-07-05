import reflex as rx
import reflex_local_auth
from .. import navigation
from ..ui.base import base_page
from ..models import BlogPostModel
from .state import BlogPostState

@reflex_local_auth.require_login
def blog_post_list_page() -> rx.Component:
    """Página que muestra la lista de posts del usuario."""
    return base_page(
        rx.vstack(
            rx.hstack(
                rx.heading("Mis Publicaciones", size="8"), rx.spacer(),
                rx.link(rx.button("Crear Nueva Publicación"), href=navigation.routes.BLOG_POST_ADD_ROUTE),
                justify="between", width="100%",
            ),
            rx.divider(margin_y="1.5em"),
            rx.grid(
                rx.foreach(
                    BlogPostState.posts,
                    lambda post: rx.link(
                        rx.card(
                            rx.vstack(
                                rx.cond(
                                    post.images,
                                    rx.image(src=f"/_upload/{post.images[0].filename}", width="100%", height="150px", object_fit="cover"),
                                    rx.box(rx.icon("image", size=48, color_scheme="gray"), width="100%", height="150px", bg=rx.color("gray", 3), display="flex", align_items="center", justify_content="center", border_radius="var(--radius-3)")
                                ),
                                rx.heading(post.title, size="4", padding_top="0.5em"),
                                align_items="start", width="100%",
                            )
                        ),
                        href=f"/blog/{post.id}/edit"
                    )
                ),
                columns=rx.breakpoints(initial="1", sm="2", md="3", lg="4"),
                spacing="4", width="100%",
            ),
            spacing="5", align="center", min_height="85vh",
            width="100%", max_width="1200px", margin="auto", padding_x="1em",
        ),
        on_mount=BlogPostState.load_posts
    )