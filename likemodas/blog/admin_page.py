# likemodas/blog/admin_page.py (Versión Final Corregida)

import reflex as rx
from ..state import AppState
from ..models import BlogPostModel
from .. import navigation
from .forms import blog_post_edit_form

def edit_post_dialog() -> rx.Component:
    """El diálogo modal que contiene el formulario de edición."""
    return rx.alert_dialog.root(
        # --- CORRECCIÓN AQUÍ ---
        # 1. El hijo `rx.alert_dialog.content` va primero.
        rx.alert_dialog.content(
            rx.alert_dialog.title("Editar Publicación"),
            rx.alert_dialog.description(
                "Modifica los detalles de tu producto y guárdalos."
            ),
            blog_post_edit_form(),
            rx.flex(
                rx.alert_dialog.cancel(
                    rx.button("Cancelar", variant="soft", color_scheme="gray")
                ),
                spacing="3",
                margin_top="1em",
                justify="end",
            ),
            # El argumento de palabra clave `style` va al final, dentro de content.
            style={"max_width": "600px"},
        ),
        # 2. Los argumentos de palabra clave `open` y `on_open_change` van después.
        open=AppState.is_editing_post,
        on_open_change=AppState.cancel_editing_post,
    )

def post_admin_row(post: BlogPostModel) -> rx.Component:
    """Componente para una fila de la tabla de administración."""
    return rx.table.row(
        rx.table.cell(
            rx.cond(
                post.image_urls & (post.image_urls.length() > 0),
                rx.avatar(src=rx.get_upload_url(post.image_urls[0]), size="4"),
                rx.box(rx.icon("image_off", size=24), width="var(--avatar-size-4)", height="var(--avatar-size-4)", bg=rx.color("gray", 3), display="flex", align_items="center", justify_content="center", border_radius="100%")
            )
        ),
        rx.table.cell(
            rx.hstack(
                rx.switch(
                    is_checked=post.publish_active,
                    # highlight-next-line
                    on_change=lambda _: AppState.toggle_publish_status(post.id),
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
                rx.button(
                    "Editar", 
                    on_click=AppState.start_editing_post(post.id),
                    variant="outline",
                    size="2"
                ),
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
                    rx.center(rx.text("Aún no tienes publicaciones."), height="50vh")
                ),
                edit_post_dialog(),
                spacing="5", width="100%",
            ),
            padding_y="2em", max_width="1200px",
        ),
        min_height="85vh",
        width="100%"
    )