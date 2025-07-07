# full_stack_python/blog/list.py

import reflex as rx 
import reflex_local_auth
from .. import navigation
from ..ui.base import base_page
from ..models import BlogPostModel
from . import state

def blog_post_list_item(post: BlogPostModel) -> rx.Component:
    """Muestra una tarjeta de publicación con imagen, título y acciones."""
    return rx.card(
        rx.vstack(
            rx.link(
                rx.vstack(
                    rx.image(
                        src=rx.get_upload_url(post.cover_image),
                        width="100%",
                        height="15em",
                        object_fit="cover",
                    ),
                    rx.heading(post.title, size="5", margin_top="0.5em"),
                    spacing="2",
                    align="start",
                ),
                href=f"{navigation.routes.BLOG_POSTS_ROUTE}/{post.id}"
            ),
            rx.spacer(),
            rx.hstack(
                rx.link(
                    rx.button("Editar", color_scheme="gray"),
                    href=f"{navigation.routes.BLOG_POSTS_ROUTE}/{post.id}/edit"
                ),
                # --- DIÁLOGO DE CONFIRMACIÓN PARA BORRAR ---
                rx.alert_dialog.root(
                    rx.alert_dialog.trigger(
                        rx.button("Eliminar", color_scheme="red")
                    ),
                    rx.alert_dialog.content(
                        rx.alert_dialog.title("Confirmar Eliminación"),
                        rx.alert_dialog.description(
                            "¿Estás seguro de que quieres eliminar esta publicación? Esta acción no se puede deshacer."
                        ),
                        rx.flex(
                            rx.alert_dialog.cancel(
                                rx.button("Cancelar", variant="soft", color_scheme="gray")
                            ),
                            rx.alert_dialog.action(
                                rx.button("Sí, eliminar", color_scheme="red", on_click=state.BlogPostState.delete_post(post.id))
                            ),
                            spacing="3",
                            margin_top="16px",
                            justify="end",
                        ),
                    ),
                ),
                justify="end",
                width="100%",
                spacing="3",
                margin_top="1em"
            ),
            height="100%",
            width="100%",
        ),
        size="2"
    )

@reflex_local_auth.require_login
def blog_post_list_page() -> rx.Component:
    return base_page(
        rx.vstack(
            rx.hstack(
                rx.heading("Mis Publicaciones", size="8"),
                rx.spacer(),
                rx.link(
                    rx.button("Crear Nuevo Post", size="3"),
                    href=navigation.routes.BLOG_POST_ADD_ROUTE
                ),
                justify="between",
                align="center",
                width="100%"
            ),
            rx.cond(
                state.BlogPostState.posts,
                rx.grid(
                    rx.foreach(state.BlogPostState.posts, blog_post_list_item),
                    columns=["1", "2", "3"], # Responsive columns
                    spacing="4",
                    width="100%",
                    margin_top="2em"
                ),
                rx.center(
                    rx.text("Aún no has creado ninguna publicación. ¡Anímate a crear una!"),
                    height="50vh"
                )
            ),
            spacing="5",
            width="100%",
            max_width="1200px",
            margin="auto",
            padding_x="1em",
            min_height="85vh",
        )
    )