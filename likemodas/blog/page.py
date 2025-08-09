# likemodas/blog/page.py (CORREGIDO)

import reflex as rx
from .state import BlogAdminState  # <-- Importamos el estado correcto
from ..models import BlogPostModel

def post_admin_row(post: BlogPostModel) -> rx.Component:
    """Componente para renderizar una fila en la tabla de administración."""
    return rx.table.row(
        rx.table.cell(
            rx.badge(
                "Publicado" if post.publish_active else "Borrador",
                color_scheme="green" if post.publish_active else "gray",
                variant="soft"
            )
        ),
        rx.table.cell(rx.link(post.title, href=f"/post/{post.id}")),
        rx.table.cell(post.publish_date_formatted), # Usamos la property del modelo
        rx.table.cell(post.price_cop),              # Usamos la property del modelo
        rx.table.cell(
            rx.hstack(
                rx.button(rx.icon("pencil"), "Editar", variant="outline"),
                rx.alert_dialog.root(
                    rx.alert_dialog.trigger(
                        rx.button(rx.icon("trash-2"), "Eliminar", color_scheme="red", variant="soft")
                    ),
                    rx.alert_dialog.content(
                        rx.alert_dialog.title("Confirmar Eliminación"),
                        rx.alert_dialog.description(
                            f"¿Seguro que quieres eliminar la publicación '{post.title}'? Esta acción es irreversible."
                        ),
                        rx.flex(
                            rx.alert_dialog.cancel(rx.button("Cancelar", variant="soft")),
                            rx.alert_dialog.action(
                                rx.button(
                                    "Sí, eliminar",
                                    color_scheme="red",
                                    on_click=lambda: BlogAdminState.delete_post(post.id)
                                )
                            ),
                            justify="end",
                            spacing="3",
                            margin_top="16px",
                        ),
                    ),
                ),
                spacing="3",
            )
        ),
        align="center",
    )

def blog_page() -> rx.Component:
    """Página de "Mis Publicaciones" para el vendedor."""
    return rx.container(
        rx.vstack(
            rx.hstack(
                rx.heading("Mis Publicaciones", size="7"),
                rx.spacer(),
                rx.button("Crear Nueva Publicación", on_click=lambda: rx.redirect("/admin/new-post")),
                justify="between",
                align="center",
                width="100%",
            ),
            rx.divider(margin_y="1.5em"),
            
            # Condición clave: Muestra la tabla si hay posts, o el mensaje si no.
            rx.cond(
                BlogAdminState.my_blog_posts,
                # Verdadero: La lista NO está vacía, muestra la tabla.
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Estado"),
                            rx.table.column_header_cell("Título"),
                            rx.table.column_header_cell("Fecha de Publicación"),
                            rx.table.column_header_cell("Precio"),
                            rx.table.column_header_cell("Acciones"),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(BlogAdminState.my_blog_posts, post_admin_row)
                    ),
                    variant="surface",
                    width="100%",
                ),
                # Falso: La lista ESTÁ vacía, muestra el mensaje de la captura.
                rx.center(
                    rx.vstack(
                        rx.icon("file-search-2", size=48, color_scheme="gray"),
                        rx.heading("No se encontraron publicaciones"),
                        rx.text("Parece que aún no has creado ninguna publicación.", color_scheme="gray"),
                        rx.button(
                            "Crear mi primera publicación", 
                            on_click=lambda: rx.redirect("/admin/new-post"),
                            margin_top="1em"
                        ),
                        spacing="3",
                        align="center",
                    ),
                    height="50vh",
                    width="100%",
                )
            ),
            spacing="5",
            width="100%",
        ),
        padding_y="2em",
        max_width="1200px",
    )