# full_stack_python/blog/list.py

import reflex as rx 
import reflex_local_auth
from .. import navigation
from ..ui.base import base_page
from ..models import BlogPostModel
from .state import BlogPostState, SessionState # Importa SessionState también

def blog_post_list_item(post: BlogPostModel):
    """Muestra un item individual de la lista de posts."""
    return rx.link(
        rx.card(
            rx.vstack(
                rx.cond(
                    post.images,
                    rx.image(
                        src=f"/_upload/{post.images[0].filename}",
                        width="100%",
                        height="150px",
                        object_fit="cover",
                    )
                ),
                rx.heading(post.title, size="4"),
                align_items="start",
            )
        ),
        href=f"/blog/{post.id}/edit",
        width="100%",
    )

@reflex_local_auth.require_login
def blog_post_list_page() -> rx.Component:
    """Página que muestra la lista de posts del usuario."""
    
    # --- CORRECCIÓN FINAL ---
    # Envolvemos la lista en un rx.cond para que solo se renderice
    # cuando el usuario está autenticado y el estado está listo.
    list_view = rx.cond(
        SessionState.is_authenticated,
        rx.grid(
            rx.foreach(BlogPostState.posts, blog_post_list_item),
            columns="3",
            spacing="4",
            width="100%",
        )
    )

    return base_page(
        rx.vstack(
            rx.heading("Mis Publicaciones", size="8"),
            rx.link(rx.button("Crear Nueva Publicación"), href="/blog/add"),
            list_view, # <-- Usamos la vista protegida
            spacing="5",
            align="center",
            min_height="85vh",
            width="100%",
        ),
        on_mount=BlogPostState.load_posts
    )