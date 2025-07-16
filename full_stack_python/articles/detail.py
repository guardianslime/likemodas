import reflex as rx
from ..ui.base import base_page
from ..blog.state import BlogPostState
from ..blog.notfound import blog_post_not_found
from .. import navigation

def article_management_detail_page() -> rx.Component:
    """
    Página de detalle para administrar un post específico.
    Muestra el contenido y las opciones para editar y eliminar.
    """
    return base_page(
        rx.cond(
            BlogPostState.post,
            rx.vstack(
                # Encabezado con título y botones de acción
                rx.hstack(
                    rx.heading(BlogPostState.post.title, size="9"),
                    rx.spacer(),
                    # Botón de Editar
                    rx.link(
                        rx.button("Editar Post", variant="soft"),
                        href=BlogPostState.blog_post_edit_url,
                    ),
                    # Botón de Eliminar con confirmación
                    rx.alert_dialog.root(
                        rx.alert_dialog.trigger(
                            rx.button("Eliminar", color_scheme="red")
                        ),
                        rx.alert_dialog.content(
                            rx.alert_dialog.title("Confirmar Eliminación"),
                            rx.alert_dialog.description(
                                f"¿Seguro que quieres eliminar '{BlogPostState.post.title}'? Esta acción es irreversible."
                            ),
                            rx.flex(
                                rx.alert_dialog.cancel(rx.button("Cancelar", variant="soft", color_scheme="gray")),
                                rx.alert_dialog.action(
                                    rx.button(
                                        "Sí, eliminar",
                                        color_scheme="red",
                                        # Usamos el nuevo método con redirección
                                        on_click=BlogPostState.delete_post_and_redirect(BlogPostState.post.id)
                                    )
                                ),
                                spacing="3",
                                margin_top="1em",
                                justify="end",
                            ),
                        ),
                    ),
                    justify="between",
                    width="100%",
                ),
                # Badges de estado y fecha
                rx.hstack(
                    rx.badge(
                        "Publicado", color_scheme="green"
                    ) if BlogPostState.post.publish_active else rx.badge(
                        "Borrador", color_scheme="gray"
                    ),
                    rx.cond(
                        BlogPostState.post.publish_date,
                        rx.text(f"Publicado el: {BlogPostState.post.publish_date_formatted}"),
                        rx.fragment(),
                    ),
                    spacing="4",
                ),
                rx.divider(),
                # Contenido del post en Markdown
                rx.markdown(BlogPostState.post.content),
                spacing="5",
                align="start",
                width="100%",
                max_width="960px",
                margin="auto",
            ),
            blog_post_not_found()
        )
    )