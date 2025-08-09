import reflex as rx
from ..state import AppState
from ..models import BlogPostModel

def post_admin_row(post: BlogPostModel) -> rx.Component:
    """Componente para renderizar una fila en la tabla de administración."""
    return rx.table.row(
        rx.table.cell(
            rx.badge(
                "Publicado" if post.publish_active else "Borrador",
                color_scheme="green" if post.publish_active else "gray",
            )
        ),
        rx.table.cell(post.title),
        rx.table.cell(post.created_at_formatted),
        rx.table.cell(
            rx.hstack(
                rx.button("Editar"),
                rx.alert_dialog.root(
                    rx.alert_dialog.trigger(
                        rx.button("Eliminar", color_scheme="red")
                    ),
                    rx.alert_dialog.content(
                        rx.alert_dialog.title("Confirmar Eliminación"),
                        rx.alert_dialog.description(f"¿Seguro que quieres eliminar '{post.title}'?"),
                        rx.flex(
                            rx.alert_dialog.cancel(rx.button("Cancelar")),
                            rx.alert_dialog.action(
                                rx.button("Sí, Eliminar", on_click=lambda: AppState.delete_post(post.id))
                            ),
                            spacing="3",
                            margin_top="1em",
                            justify="end",
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
    return rx.container(
        rx.vstack(
            rx.hstack(
                rx.heading("Mis Publicaciones", size="7"),
                rx.spacer(),
                rx.button("Crear Nueva Publicación"),
                justify="between",
                align="center",
                width="100%",
            ),
            rx.divider(margin_y="1.5em"),
            rx.cond(
                AppState.my_admin_posts,
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Estado"),
                            rx.table.column_header_cell("Título"),
                            rx.table.column_header_cell("Fecha"),
                            rx.table.column_header_cell("Acciones"),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(AppState.my_admin_posts, post_admin_row)
                    ),
                    variant="surface",
                    width="100%",
                ),
                rx.center(
                    rx.text("No has creado ninguna publicación todavía."),
                    height="50vh",
                )
            ),
            spacing="5",
            width="100%",
        ),
        padding_y="2em",
    )