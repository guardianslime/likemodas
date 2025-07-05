# full_stack_python/blog/list.py

import reflex as rx 
import reflex_local_auth
from .. import navigation
from ..ui.base import base_page
from ..models import BlogPostModel
from .state import BlogPostState, SessionState

def blog_post_list_item(post: BlogPostModel):
    """Muestra un item individual de la lista de posts del blog."""
    return rx.link(
        rx.card(
            rx.vstack(
                # Muestra la primera imagen como miniatura si existe
                rx.cond(
                    post.images,
                    rx.image(
                        src=f"/_upload/{post.images[0].filename}",
                        width="100%",
                        height="150px",
                        object_fit="cover",
                    ),
                    # Muestra un placeholder si no hay imagen
                    rx.box(
                        rx.icon("image", size=48, color="gray"),
                        width="100%",
                        height="150px",
                        bg=rx.color("gray", 3),
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        border_radius="var(--radius-3)",
                    )
                ),
                rx.heading(post.title, size="4", padding_top="0.5em"),
                align_items="start",
                width="100%",
            )
        ),
        href=f"/blog/{post.id}/edit", # Enlaza a la página de edición
        width="100%",
    )

@reflex_local_auth.require_login
def blog_post_list_page() -> rx.Component:
    """Página que muestra la lista de posts del usuario."""
    
    # --- CORRECCIÓN FINAL Y DEFINITIVA ---
    # La lista de posts solo se renderiza si el usuario está autenticado.
    # Esto asegura que el estado esté listo y evita el `AttributeError`.
    list_view = rx.cond(
        SessionState.is_authenticated,
        rx.grid(
            rx.foreach(BlogPostState.posts, blog_post_list_item),
            columns=["1", "2", "3", "4"], # Columnas responsivas
            spacing="4",
            width="100%",
        ),
        # Muestra un spinner mientras carga o si no está autenticado
        rx.spinner(size="3")
    )

    return base_page(
        rx.vstack(
            rx.hstack(
                rx.heading("Mis Publicaciones", size="8"),
                rx.spacer(),
                rx.link(rx.button("Crear Nueva Publicación"), href="/blog/add"),
                justify="between",
                width="100%",
            ),
            rx.divider(margin_y="1.5em"),
            list_view, # <-- Se usa la vista protegida por la condición
            spacing="5",
            align="center",
            min_height="85vh",
            width="100%",
            max_width="1200px",
            margin="auto",
            padding_x="1em",
        ),
        # El evento on_mount es la forma más segura de cargar los datos
        on_mount=BlogPostState.load_posts
    )