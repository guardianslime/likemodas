# likemodas/blog/admin_page.py (ARCHIVO FINAL CORREGIDO)

import reflex as rx
from ..state import AppState
from ..models import BlogPostModel
from .. import navigation  # Importamos navigation para las rutas

def post_admin_row(post: BlogPostModel) -> rx.Component:
    """Componente que renderiza una fila en la tabla de administración."""
    return rx.table.row(
        rx.table.cell(
            # --- INICIO DE LA CORRECCIÓN ---
            # Usamos rx.cond para manejar la lógica condicional en la UI.
            # rx.cond(condición, valor_si_verdadero, valor_si_falso)
            rx.badge(
                rx.cond(post.publish_active, "Publicado", "Borrador"),
                color_scheme=rx.cond(post.publish_active, "green", "gray"),
                variant="soft"
            )
            # --- FIN DE LA CORRECCIÓN ---
        ),
        rx.table.cell(post.title, max_width="250px", overflow="hidden", text_overflow="ellipsis"),
        rx.table.cell(post.created_at_formatted),
        rx.table.cell(post.price_cop),
        rx.table.cell(
            rx.hstack(
                # El botón Editar debería redirigir a la página de edición del post
                rx.button(
                    "Editar", 
                    on_click=rx.redirect(f"/blog/{post.id}/edit"),
                    variant="outline",
                    size="2"
                ),
                rx.alert_dialog.root(
                    rx.alert_dialog.trigger(
                        rx.button("Eliminar", color_scheme="red", variant="soft", size="2")
                    ),
                    rx.alert_dialog.content(
                        rx.alert_dialog.title("Confirmar Eliminación"),
                        rx.alert_dialog.description(
                            f"¿Seguro que quieres eliminar la publicación '{post.title}'? Esta acción es irreversible."
                        ),
                        rx.flex(
                            rx.alert_dialog.cancel(rx.button("Cancelar", variant="soft", color_scheme="gray")),
                            rx.alert_dialog.action(
                                rx.button(
                                    "Sí, Eliminar",
                                    color_scheme="red",
                                    on_click=lambda: AppState.delete_post(post.id)
                                )
                            ),
                            spacing="3",
                            margin_top="16px",
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
                rx.button(
                    "Crear Nueva Publicación", 
                    on_click=rx.redirect(navigation.routes.BLOG_POST_ADD_ROUTE)
                ),
                justify="between",
                align="center",
                width="100%",
            ),
            rx.divider(margin_y="1.5em"),
            
            # Condición para mostrar la tabla o un mensaje si no hay posts.
            rx.cond(
                AppState.my_admin_posts,
                # Verdadero: La lista NO está vacía, muestra la tabla.
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Estado"),
                            rx.table.column_header_cell("Título"),
                            rx.table.column_header_cell("Fecha Creación"),
                            rx.table.column_header_cell("Precio"),
                            rx.table.column_header_cell("Acciones"),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(AppState.my_admin_posts, post_admin_row)
                    ),
                    variant="surface",
                    width="100%",
                ),
                # Falso: La lista ESTÁ vacía, muestra el mensaje.
                rx.center(
                    rx.vstack(
                        rx.icon("file-search-2", size=48, color_scheme="gray"),
                        rx.heading("Aún no tienes publicaciones"),
                        rx.text("¡Crea tu primera publicación para que aparezca aquí!", color_scheme="gray"),
                        rx.button(
                            "Crear mi primera publicación", 
                            on_click=rx.redirect(navigation.routes.BLOG_POST_ADD_ROUTE),
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