# likemodas/blog/admin_page.py (COMPLETO Y CORREGIDO)

import reflex as rx
from ..state import AppState
from .. import navigation
from .forms import blog_post_edit_form
from ..state import AppState, AdminPostRowData, AdminVariantData
from ..ui.qr_display import qr_code_display

def edit_post_dialog() -> rx.Component:
    """El diálogo modal que contiene el formulario de edición."""
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Editar Publicación"),
            rx.alert_dialog.description("Modifica los detalles de tu producto y guárdalos."),
            blog_post_edit_form(),
            rx.flex(
                rx.alert_dialog.cancel(
                    rx.button("Cancelar", variant="soft", color_scheme="gray")
                ),
                spacing="3",
                margin_top="1em",
                justify="end",
            ),
            style={"max_width": "960px"},
        ),
        open=AppState.is_editing_post,
        on_open_change=AppState.cancel_editing_post,
    )

def qr_display_modal() -> rx.Component:
    """El diálogo modal que muestra los códigos QR para cada variante."""
    printable_area_style = {
        "id": "printable-qr-area",
        "@media print": {
            "body *": {
                "visibility": "hidden",
            },
            "#printable-qr-area, #printable-qr-area *": {
                "visibility": "visible",
            },
            "#printable-qr-area": {
                "position": "absolute",
                "left": "0",
                "top": "0",
                "right": "0",
                "bottom": "0",
                "margin": "auto",
                "padding": "20px",
            },
        },
    }
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Códigos QR de Variantes"),
            rx.dialog.description(
                "Escanea o imprime estos códigos QR para acceder rápidamente a cada variante del producto."
            ),
            rx.box(
                rx.grid(
                    rx.foreach(
                        AppState.qr_codes_for_post,
                        lambda variant: qr_code_display(
                            variant=variant,
                            product_title=AppState.editing_post_title,
                        ),
                    ),
                    columns=["1", "2", "3"],
                    spacing="4",
                    width="100%",
                ),
                **printable_area_style,
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button("Cerrar", variant="soft", color_scheme="gray"),
                ),
                rx.button("Imprimir", on_click=rx.call_script("window.print()")),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
        ),
        open=AppState.is_showing_qr,
        on_open_change=AppState.set_is_showing_qr,
    )

def post_admin_row(post: AdminPostRowData) -> rx.Component:
    """Renderiza una fila en la tabla de administración de posts."""
    return rx.table.row(
        rx.table.cell(
            rx.avatar(src=rx.get_upload_url(post.main_image), fallback=post.title[0], size="4")
        ),
        rx.table.cell(
            rx.badge(
                post.publication_status,
                color_scheme="grass" if post.publication_status == "Publicado" else "amber",
            )
        ),
        # --- MODIFICACIÓN PARA EL TÍTULO ---
        rx.table.cell(
            rx.text(
                post.title,
                white_space="normal",
                max_width=["150px", "200px", "300px", "400px", "500px"],
            )
        ),
        rx.table.cell(rx.text(post.price_cop)),
        rx.table.cell(
            rx.hstack(
                rx.icon_button(
                    "pencil",
                    on_click=AppState.start_editing_post(post.id),
                    variant="soft",
                    color_scheme="gray",
                ),
                rx.icon_button(
                    "trash-2",
                    on_click=AppState.delete_blog_post(post.id),
                    variant="soft",
                    color_scheme="red",
                ),
            )
        ),
        rx.table.cell(
            rx.icon_button(
                "qr-code",
                on_click=AppState.show_qr_for_post(post.id, post.title),
                variant="soft",
            )
        ),
    )

def my_posts_page() -> rx.Component:
    """La página principal para que los administradores gestionen sus publicaciones."""
    return rx.box(
        rx.center(
            rx.vstack(
                rx.hstack(
                    rx.heading("Mis Publicaciones", size="8"),
                    rx.spacer(),
                    rx.button("Crear Publicación", on_click=rx.redirect(navigation.routes.BLOG_POST_ADD_ROUTE), color_scheme="violet"),
                    justify="between", align="center", width="100%",
                ),
                rx.divider(margin_y="1.5em"),
                rx.cond(
                    AppState.my_admin_posts,
                    # --- MODIFICACIÓN: ENVOLVER TABLA EN SCROLL_AREA ---
                    rx.scroll_area(
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Imagen"),
                                    rx.table.column_header_cell("Estado"),
                                    rx.table.column_header_cell("Título"),
                                    rx.table.column_header_cell("Precio"),
                                    rx.table.column_header_cell("Acciones"),
                                    rx.table.column_header_cell("QR"),
                                )
                            ),
                            rx.table.body(
                                rx.foreach(AppState.my_admin_posts, post_admin_row)
                            ),
                            variant="surface", width="100%",
                        ),
                        scrollbars="horizontal",
                    ),
                    rx.center(rx.text("Aún no tienes publicaciones."), height="50vh")
                ),
                edit_post_dialog(),
                qr_display_modal(),
                spacing="5", width="100%",
            ),
            padding_y="2em", max_width="1200px",
        ),
        min_height="85vh",
        width="100%"
    )