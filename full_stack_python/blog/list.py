# full_stack_python/blog/list.py (CORREGIDO)

import reflex as rx
import reflex_local_auth
from ..ui.base import base_page
from ..models import BlogPostModel
from .. import navigation
from .state import BlogPostState

def blog_post_list_item(post: BlogPostModel):
    return rx.link(
        rx.card(
            rx.vstack(
                rx.heading(post.title, size="4"),
                rx.cond(
                    post.publish_active,
                    rx.badge("Publicado", color_scheme="green"),
                    rx.badge("Borrador", color_scheme="gray")
                ),
                # --- ✨ CORRECCIÓN AQUÍ ✨ ---
                # Usamos la nueva propiedad 'created_at_formatted' en lugar de llamar a .strftime()
                rx.text(f"Creado: {post.created_at_formatted}", size="2"),
                align="start",
            )
        ),
        href=f"{navigation.routes.BLOG_POSTS_ROUTE}/{post.id}"
    )

# ... (El resto del archivo 'blog_post_list_page' no necesita cambios) ...
@reflex_local_auth.require_login
def blog_post_list_page() -> rx.Component:
    return base_page(
        rx.vstack(
            rx.hstack(
                rx.heading("Mis Posts", size="7"),
                rx.spacer(),
                rx.link(rx.button("Nuevo Post"), href=navigation.routes.BLOG_POST_ADD_ROUTE),
                justify="between",
                width="100%"
            ),
            rx.divider(),
            rx.cond(
                BlogPostState.posts,
                rx.grid(
                    rx.foreach(BlogPostState.posts, blog_post_list_item),
                    columns=[1, 2, 3],
                    spacing="4"
                ),
                rx.center(rx.text("Aún no has escrito ningún post."), padding_y="4em")
            ),
            spacing="4",
            width="100%",
            max_width="960px",
            margin="auto",
        )
    )