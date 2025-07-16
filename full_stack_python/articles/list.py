import reflex as rx 
import reflex_local_auth
from .. import navigation
from ..ui.base import base_page
from ..models import BlogPostModel
from . import state
from ..blog.state import BlogPostState

import reflex as rx
import reflex_local_auth
from ..ui.base import base_page
from ..models import BlogPostModel
from .. import navigation
from ..blog.state import BlogPostState

def blog_post_management_card(post: BlogPostModel) -> rx.Component:
    """
    Una tarjeta de gestión para una publicación de blog.
    Muestra la imagen, título, estado y botones de acción.
    """
    return rx.card(
        rx.vstack(
            # Sección de la imagen, similar a blog/page.py
            rx.box(
                rx.cond(
                    post.images & (post.images.length() > 0),
                    rx.image(
                        src=rx.get_upload_url(post.images[0]),
                        width="100%",
                        height="200px",
                        object_fit="cover",
                        border_radius="md",
                    ),
                    rx.box(
                        rx.text("Sin imagen"),
                        display="flex",
                        align="center",
                        justify="center",
                        height="200px",
                        bg="#eee",
                        border_radius="md",
                    )
                ),
                width="100%",
            ),
            # Información del post
            rx.vstack(
                rx.heading(post.title, size="4", trim="both"),
                rx.badge(
                    "Publicado", color_scheme="green"
                ) if post.publish_active else rx.badge(
                    "Borrador", color_scheme="gray"
                ),
                align="start",
                spacing="2",
                width="100%",
                padding_y="0.5em",
            ),
            rx.spacer(),
            # Botones de Acción
            rx.hstack(
                rx.link(
                    rx.button("Editar", variant="soft"),
                    href=f"{navigation.routes.BLOG_POSTS_ROUTE}/{post.id}/edit",
                    width="50%"
                ),
                # Botón de eliminar con diálogo de confirmación
                rx.alert_dialog.root(
                    rx.alert_dialog.trigger(
                        rx.button("Eliminar", color_scheme="red", width="50%")
                    ),
                    rx.alert_dialog.content(
                        rx.alert_dialog.title("Confirmar Eliminación"),
                        rx.alert_dialog.description(
                            f"¿Estás seguro de que quieres eliminar la publicación '{post.title}'? Esta acción no se puede deshacer."
                        ),
                        rx.flex(
                            rx.alert_dialog.cancel(
                                rx.button("Cancelar", variant="soft", color_scheme="gray")
                            ),
                            rx.alert_dialog.action(
                                rx.button(
                                    "Sí, eliminar", 
                                    color_scheme="red",
                                    on_click=BlogPostState.delete_post(post.id)
                                )
                            ),
                            spacing="3",
                            margin_top="1em",
                            justify="end",
                        ),
                    ),
                ),
                spacing="2",
                width="100%",
            ),
            spacing="2",
            height="100%",
        ),
        size="2"
    )

@reflex_local_auth.require_login
def manage_blog_posts_page() -> rx.Component:
    """Página para que los usuarios administren sus publicaciones de blog."""
    return base_page(
        rx.vstack(
            rx.hstack(
                rx.heading("Administrar Mis Publicaciones", size="7"),
                rx.spacer(),
                rx.link(
                    rx.button("Crear Nuevo Post"), 
                    href=navigation.routes.BLOG_POST_ADD_ROUTE
                ),
                justify="between",
                width="100%"
            ),
            rx.divider(),
            rx.cond(
                BlogPostState.posts,
                rx.grid(
                    rx.foreach(BlogPostState.posts, blog_post_management_card),
                    columns="repeat(auto-fit, minmax(300px, 1fr))",
                    spacing="4",
                    width="100%",
                ),
                rx.center(
                    rx.text("Aún no has creado ninguna publicación."), 
                    padding_y="4em"
                )
            ),
            spacing="4",
            width="100%",
            max_width="1200px",
            margin="auto",
        )
    )

def article_card_link(post: BlogPostModel):
    post_id = post.id
    if post_id is None:
        return rx.fragment("Not found")
    root_path = navigation.routes.ARTICLE_LIST_ROUTE
    post_detail_url = f"{root_path}/{post_id}"
    return rx.card(
        rx.link(
            rx.flex(
                rx.box(
                    rx.heading(post.title),
                ),
                spacing="2",
            ),
            href=post_detail_url
        ), 
        as_child=True
    )

def article_public_list_component(columns:int=3, spacing:int=5, limit:int=100) -> rx.Component:
    return rx.grid(
        rx.foreach(state.ArticlePublicState.posts,article_card_link),
        columns=f'{columns}',
        spacing= f'{spacing}',
        on_mount=lambda: state.ArticlePublicState.set_limit_and_reload(limit)
    )

def article_public_list_page() -> rx.Component:
    return base_page(
        rx.box(
            rx.heading("Published Articles", size="5"),
            article_public_list_component(),      
            min_height="85vh",
        )
    )