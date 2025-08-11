# likemodas/blog/admin_page.py (CON LA SINTAXIS CORRECTA rx.el.*)

import reflex as rx
from ..state import AppState
from ..models import BlogPostModel
from .. import navigation

def post_admin_row(post: BlogPostModel) -> rx.Component:
    """Fila de la tabla de admin con la sintaxis correcta de rx.el.*."""
    # --- Se usa la sintaxis rx.el.tr y rx.el.td ---
    return rx.el.tr(
        rx.el.td(
            rx.cond(
                post.image_urls & (post.image_urls.length() > 0),
                rx.avatar(src=rx.get_upload_url(post.image_urls[0]), size="4"),
                rx.avatar(fallback="?", size="4")
            )
        ),
        rx.el.td(
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
        rx.el.td(post.title),
        rx.el.td(post.price_cop),
        rx.el.td(
            rx.hstack(
                rx.button(
                    "Editar",
                    on_click=rx.redirect(f"/blog/{post.id}/edit"),
                    variant="outline",
                    size="sm"
                ),
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
                rx.button(
                    "Eliminar",
                    on_click=rx.set_value(f"delete-dialog-{post.id}", True),
                    color_scheme="red",
                    variant="ghost",
                    size="sm"
                ),
                spacing="3",
            )
        ),
        style={"vertical_align": "middle"},
    )

def blog_admin_page() -> rx.Component:
    """Página de 'Mis Publicaciones' para el vendedor."""
    return rx.center(
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
                    # --- Se usa la sintaxis rx.el.table y sus hijos ---
                    rx.el.table(
                        rx.el.thead(
                            rx.el.tr(
                                rx.el.th("Imagen"),
                                rx.el.th("Estado"),
                                rx.el.th("Título"),
                                rx.el.th("Precio"),
                                rx.el.th("Acciones"),
                            )
                        ),
                        rx.el.tbody(
                            rx.foreach(AppState.my_admin_posts, post_admin_row)
                        ),
                        width="100%",
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