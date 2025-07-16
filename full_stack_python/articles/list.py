import reflex as rx
import reflex_local_auth
from ..ui.base import base_page
from ..models import BlogPostModel
from .. import navigation
from ..blog.state import BlogPostState

def _management_card(post: BlogPostModel) -> rx.Component:
    return rx.link(
        rx.card(
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
                        bg=rx.color("gray", 3),
                        border_radius="md",
                    ),
                ),
                rx.alert_dialog.root(
                    rx.alert_dialog.trigger(
                        rx.icon_button(
                            "trash-2",
                            position="absolute",
                            top="0.5em",
                            right="0.5em",
                            bg="rgba(255, 255, 255, 0.7)",
                            color="red",
                            variant="soft",
                            on_click=lambda e: e.stop_propagation(),
                        )
                    ),
                    rx.alert_dialog.content(
                        rx.alert_dialog.title("Confirmar Eliminación"),
                        rx.alert_dialog.description(
                            f"¿Seguro que quieres eliminar '{post.title}'? No podrás recuperarlo."
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
                position="relative",
            ),
            rx.text(post.title, weight="bold", size="3", mt="0.5em"),
            footer=rx.badge(
                "Publicado", color_scheme="green"
            ) if post.publish_active else rx.badge(
                "Borrador", color_scheme="gray"
            ),
            style={"_hover": {"transform": "scale(1.03)", "transition": "transform 0.2s ease-in-out"}},
        ),
        href=f"{navigation.routes.ARTICLE_LIST_ROUTE}/{post.id}",
    )

@reflex_local_auth.require_login
def manage_blog_posts_page() -> rx.Component:
    """Página para que los usuarios administren sus publicaciones de blog."""
    return base_page(
        rx.vstack(
            rx.hstack(
                rx.heading("Administrar Mis Publicaciones", size="7"),
                rx.spacer(),
                rx.link(rx.button("Crear Nuevo Post"), href=navigation.routes.BLOG_POST_ADD_ROUTE),
                justify="between",
                width="100%",
            ),
            rx.divider(),
            rx.cond(
                BlogPostState.posts,
                rx.grid(
                    rx.foreach(BlogPostState.posts, _management_card),
                    columns="repeat(auto-fit, minmax(280px, 1fr))",
                    spacing="4",
                    width="100%",
                ),
                rx.center(
                    rx.text("Aún no has creado ninguna publicación."),
                    padding_y="4em"
                ),
            ),
            spacing="4",
            width="100%",
            max_width="1200px",
            margin="auto",
        )
    )