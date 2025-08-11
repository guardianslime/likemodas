# likemodas/blog/admin_page.py (ACTUALIZADO CON MÁS FUNCIONALIDAD)

import reflex as rx
from ..state import AppState
from ..models import BlogPostModel
from .. import navigation

def post_admin_row(post: BlogPostModel) -> rx.Component:
    """Componente mejorado para una fila de la tabla de administración con imagen."""
    return rx.table.row(
        rx.table.cell(
            # Columna para la imagen
            rx.cond(
                post.image_urls & (post.image_urls.length() > 0),
                rx.avatar(src=rx.get_upload_url(post.image_urls[0]), size="4"),
                rx.avatar(fallback=rx.icon("image_off"), size="4")
            )
        ),
        rx.table.cell(
            # Switch para habilitar/inhabilitar la publicación
            rx.hstack(
                rx.switch(
                    is_checked=post.publish_active,
                    on_change=lambda checked: AppState.toggle_publish_status(post.id),
                ),
                rx.text(rx.cond(post.publish_active, "Visible", "Oculto")),
                spacing="2",
                align="center",
            )
        ),
        rx.table.cell(post.title),
        rx.table.cell(post.price_cop),
        rx.table.cell(
            rx.hstack(
                # Botón Editar
                rx.button(
                    "Editar", 
                    on_click=rx.redirect(f"/blog/{post.id}/edit"),
                    variant="outline",
                    size="2"
                ),
                # Botón Eliminar
                rx.alert_dialog.root(
                    rx.alert_dialog.trigger(
                        rx.button("Eliminar", color_scheme="red", variant="soft", size="2")
                    ),
                    rx.alert_dialog.content(
                        rx.alert_dialog.title("Confirmar Eliminación"),
                        rx.alert_dialog.description(f"¿Seguro que quieres eliminar '{post.title}'?"),
                        rx.flex(
                            rx.alert_dialog.cancel(rx.button("Cancelar")),
                            rx.alert_dialog.action(
                                rx.button("Sí, Eliminar", on_click=lambda: AppState.delete_post(post.id))
                            ),
                            spacing="3", margin_top="1em", justify="end",
                        ),
                    ),
                ),
                spacing="3",
            )
        ),
        align="center",
    )

def blog_admin_page() -> rx.Component:
    """Página de 'Mis Publicaciones' para el vendedor."""
    # Envolvemos el contenido en un rx.center para asegurar la alineación vertical.
    return rx.center(
        rx.container(
            rx.vstack(
                rx.hstack(
                    rx.heading("Mis Publicaciones", size="7"),
                    rx.spacer(),
                    rx.button("Crear Nueva Publicación", on_click=rx.redirect(navigation.routes.BLOG_POST_ADD_ROUTE)),
                    justify="between", align="center", width="100%",
                ),
                rx.divider(margin_y="1.5em"),
                rx.cond(
                    AppState.my_admin_posts,
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                # Nueva cabecera de columna para la imagen
                                rx.table.column_header_cell("Imagen"),
                                rx.table.column_header_cell("Estado"),
                                rx.table.column_header_cell("Título"),
                                rx.table.column_header_cell("Precio"),
                                rx.table.column_header_cell("Acciones"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(AppState.my_admin_posts, post_admin_row)
                        ),
                        variant="surface", width="100%",
                    ),
                    rx.center(
                        rx.vstack(
                            rx.icon("file-search-2", size=48),
                            rx.heading("Aún no tienes publicaciones"),
                            rx.button("Crear mi primera publicación", on_click=rx.redirect(navigation.routes.BLOG_POST_ADD_ROUTE), margin_top="1em"),
                            spacing="3", align="center",
                        ),
                        height="50vh", width="100%",
                    )
                ),
                spacing="5", width="100%",
            ),
            padding_y="2em", max_width="1200px",
        ),
        min_height="85vh", # Asegura que ocupe al menos el 85% de la altura de la ventana
        width="100%"
    )