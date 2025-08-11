# likemodas/blog/admin_page.py (CORREGIDO CON rx.chakra)

import reflex as rx
from ..state import AppState
from ..models import BlogPostModel
from .. import navigation

def post_admin_row(post: BlogPostModel) -> rx.Component:
    """Fila de la tabla de admin con sintaxis de rx.chakra."""
    # --- CAMBIO CLAVE: Se usa rx.chakra.tr y rx.chakra.td ---
    return rx.chakra.tr(
        rx.chakra.td(
            rx.cond(
                post.image_urls & (post.image_urls.length() > 0),
                rx.chakra.avatar(src=rx.get_upload_url(post.image_urls[0]), size="md"),
                rx.chakra.avatar(fallback="?", size="md")
            )
        ),
        rx.chakra.td(
            rx.chakra.hstack(
                rx.chakra.switch(
                    is_checked=post.publish_active,
                    on_change=lambda checked: AppState.toggle_publish_status(post.id),
                ),
                rx.chakra.text(rx.cond(post.publish_active, "Visible", "Oculto")),
                spacing="2",
                align_items="center",
            )
        ),
        rx.chakra.td(post.title),
        rx.chakra.td(post.price_cop),
        rx.chakra.td(
            rx.chakra.hstack(
                rx.chakra.button(
                    "Editar",
                    on_click=rx.redirect(f"/blog/{post.id}/edit"),
                    variant="outline",
                    size="sm"
                ),
                # Nota: El alert_dialog también puede necesitar el prefijo chakra si da error.
                rx.alert_dialog(
                    rx.alert_dialog_overlay(
                        rx.alert_dialog_content(
                            rx.alert_dialog_header("Confirmar Eliminación"),
                            rx.alert_dialog_body(f"¿Seguro que quieres eliminar '{post.title}'?"),
                            rx.alert_dialog_footer(
                                rx.button("Cancelar", on_click=rx.cancel_alert),
                                rx.button("Sí, Eliminar", on_click=lambda: AppState.delete_post(post.id)),
                            ),
                        )
                    ),
                    id=f"delete-dialog-{post.id}"
                ),
                rx.chakra.button(
                    "Eliminar",
                    on_click=rx.set_value(f"delete-dialog-{post.id}", True),
                    color_scheme="red",
                    variant="ghost",
                    size="sm"
                ),
                spacing="3",
            )
        ),
        vertical_align="middle",
    )

def blog_admin_page() -> rx.Component:
    """Página de 'Mis Publicaciones' para el vendedor."""
    return rx.chakra.center(
        rx.chakra.container(
            rx.chakra.vstack(
                rx.chakra.hstack(
                    rx.chakra.heading("Mis Publicaciones", font_size="2em"),
                    rx.chakra.spacer(),
                    rx.chakra.button("Crear Nueva Publicación", on_click=rx.redirect(navigation.routes.BLOG_POST_ADD_ROUTE)),
                    justify="between", align="center", width="100%",
                ),
                rx.chakra.divider(margin_y="1.5em"),
                rx.cond(
                    AppState.my_admin_posts,
                    # --- CAMBIO CLAVE: Se usa rx.chakra.table y sus hijos ---
                    rx.chakra.table(
                        rx.chakra.thead(
                            rx.chakra.tr(
                                rx.chakra.th("Imagen"),
                                rx.chakra.th("Estado"),
                                rx.chakra.th("Título"),
                                rx.chakra.th("Precio"),
                                rx.chakra.th("Acciones"),
                            )
                        ),
                        rx.chakra.tbody(
                            rx.foreach(AppState.my_admin_posts, post_admin_row)
                        ),
                        variant="simple", width="100%",
                    ),
                    rx.chakra.center(
                        rx.chakra.vstack(
                            rx.icon("file-search-2", size=48),
                            rx.chakra.heading("Aún no tienes publicaciones"),
                            rx.chakra.button("Crear mi primera publicación", on_click=rx.redirect(navigation.routes.BLOG_POST_ADD_ROUTE), margin_top="1em"),
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