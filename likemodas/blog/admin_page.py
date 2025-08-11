# likemodas/blog/admin_page.py (CON DIÁLOGO MANUAL)

import reflex as rx
from ..state import AppState
from ..models import BlogPostModel
from .. import navigation

def confirm_delete_dialog() -> rx.Component:
    """Un diálogo de confirmación de borrado construido manualmente."""
    # Obtenemos el post que se va a borrar del estado
    post_to_delete = AppState.get_post_by_id(AppState.show_confirm_delete_dialog_id)
    post_title = rx.cond(post_to_delete, post_to_delete.title, "este elemento")

    return rx.cond(
        AppState.show_confirm_delete_dialog_id.is_not_none(),
        rx.box(
            # Contenido del diálogo
            rx.vstack(
                rx.heading("Confirmar Eliminación"),
                rx.text(f"¿Seguro que quieres eliminar '{post_title}'? Esta acción no se puede deshacer."),
                rx.hstack(
                    rx.button("Cancelar", on_click=AppState.hide_delete_dialog, variant="ghost"),
                    rx.button("Sí, Eliminar", on_click=AppState.delete_post(AppState.show_confirm_delete_dialog_id)),
                    justify="end",
                    width="100%",
                    margin_top="1em"
                ),
                bg="white",
                padding="2em",
                border_radius="md",
                box_shadow="lg",
                spacing="4",
            ),
            # Fondo oscuro semitransparente
            position="fixed",
            top="0",
            left="0",
            width="100%",
            height="100%",
            bg="rgba(0, 0, 0, 0.5)",
            display="flex",
            align_items="center",
            justify_content="center",
            z_index="2000",
        )
    )

def post_admin_row(post: BlogPostModel) -> rx.Component:
    """Fila de la tabla de admin con el nuevo botón de borrado."""
    return rx.tr(
        rx.td(
            rx.cond(
                post.image_urls & (post.image_urls.length() > 0),
                rx.avatar(src=rx.get_upload_url(post.image_urls[0]), size="4"),
                rx.avatar(fallback="?", size="4")
            )
        ),
        rx.td(
            rx.hstack(
                rx.switch(
                    is_checked=post.publish_active,
                    on_change=lambda checked: AppState.toggle_publish_status(post.id),
                ),
                rx.text(rx.cond(post.publish_active, "Visible", "Oculto")),
                spacing="2",
                align_items="center",
            )
        ),
        rx.td(post.title),
        rx.td(post.price_cop),
        rx.td(
            rx.hstack(
                rx.button(
                    "Editar",
                    on_click=rx.redirect(f"/blog/{post.id}/edit"),
                    variant="outline",
                    size="2"
                ),
                # --- CAMBIO: El botón ahora llama a nuestro método del estado ---
                rx.button(
                    "Eliminar",
                    on_click=AppState.show_delete_dialog(post.id),
                    color_scheme="red",
                    variant="ghost",
                    size="2"
                ),
                spacing="3",
            )
        ),
        vertical_align="middle",
    )

def blog_admin_page() -> rx.Component:
    """Página de 'Mis Publicaciones' con el diálogo de borrado."""
    return rx.fragment(
        # El diálogo se pone aquí, fuera de la tabla, para que se renderice correctamente
        confirm_delete_dialog(),
        rx.center(
            rx.container(
                rx.vstack(
                    rx.hstack(
                        rx.heading("Mis Publicaciones", font_size="2em"),
                        rx.spacer(),
                        rx.button("Crear Nueva Publicación", on_click=rx.redirect(navigation.routes.BLOG_POST_ADD_ROUTE)),
                        justify="between", align="center", width="100%",
                    ),
                    rx.divider(margin_y="1.5em"),
                    rx.cond(
                        AppState.my_admin_posts,
                        rx.table(
                            rx.thead(
                                rx.tr(
                                    rx.th("Imagen"),
                                    rx.th("Estado"),
                                    rx.th("Título"),
                                    rx.th("Precio"),
                                    rx.th("Acciones"),
                                )
                            ),
                            rx.tbody(
                                rx.foreach(AppState.my_admin_posts, post_admin_row)
                            ),
                            variant="simple", width="100%",
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
            min_height="85vh",
            width="100%"
        )
    )