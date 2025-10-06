import reflex as rx

from likemodas.ui.qr_display import qr_code_display
from ..auth.admin_auth import require_admin
from .. import navigation
from ..state import AdminVariantData, AppState, AdminPostRowData

# --- PASO 1: Importar los componentes del modal y formulario desde un archivo separado ---
# (Esto asume que los tienes en un archivo como se muestra en tu código base)
from .forms import blog_post_edit_form, edit_post_dialog
from .admin_page import qr_display_modal, mobile_post_card, desktop_post_row

def edit_post_dialog() -> rx.Component:
    """El diálogo modal que contiene el formulario de edición."""
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            # --- INICIO DE LA MODIFICACIÓN: AÑADIR BOTÓN DE CIERRE 'X' ---
            rx.alert_dialog.cancel(
                rx.icon_button(
                    rx.icon(tag="x"),
                    variant="soft",
                    color_scheme="gray",
                    style={
                        "position": "absolute",
                        "top": "0.8rem",
                        "right": "0.8rem",
                    },
                )
            ),
            # --- FIN DE LA MODIFICACIÓN ---
            
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
            "body > *:not(#printable-qr-area)": {"display": "none"},
            "#printable-qr-area": {
                "position": "absolute",
                "left": "0",
                "top": "0",
                "width": "100%",
                "padding": "1em",
            },
        },
    }

    def render_variant_qr(variant: AdminVariantData) -> rx.Component:
        """Renderiza la fila para una variante, mostrando un único código QR."""
        return rx.box(
            rx.hstack(
                rx.vstack(
                    rx.text(variant.attributes_str, weight="bold", size="4"),
                    rx.text(f"Stock: {variant.stock}"),
                    align_items="start",
                    spacing="1",
                    flex_grow="1",
                ),
                rx.spacer(),
                rx.vstack(
                    rx.text("Código QR Único", size="2", weight="medium"),
                    rx.cond(
                        variant.qr_url != "",
                        qr_code_display(value=variant.qr_url, size=120),
                        rx.center(rx.text("Sin QR"), width="120px", height="120px")
                    ),
                    rx.text(variant.variant_uuid, size="1", color_scheme="gray", no_of_lines=1, max_width="140px"),
                    align="center",
                ),
                spacing="6",
                align="center",
                width="100%"
            ),
            border="1px solid",
            border_color=rx.color("gray", 6),
            border_radius="md",
            padding="1em",
            width="100%",
        )

    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.dialog.title(
                        "Códigos QR para: ",
                        rx.text(
                            AppState.post_for_qr_display.title,
                            as_="span",
                            color_scheme="violet"
                        )
                    ),
                    rx.spacer(),
                    rx.button("Imprimir", on_click=rx.call_script("window.print()")),
                    justify="between",
                    width="100%"
                ),
                rx.dialog.description("Cada código QR identifica una variante única de tu producto."),
                rx.scroll_area(
                    rx.vstack(
                        rx.foreach(
                            AppState.post_for_qr_display.variants,
                            render_variant_qr
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    max_height="60vh",
                    type="auto",
                    scrollbars="vertical",
                ),
                rx.flex(
                    rx.dialog.close(
                        rx.button("Cerrar", variant="soft", color_scheme="gray")
                    ),
                    spacing="3",
                    margin_top="1em",
                    justify="end",
                ),
                align_items="stretch",
                spacing="4",
                style=printable_area_style,
            ),
            style={"max_width": "720px"},
        ),
        open=AppState.show_qr_display_modal,
        on_open_change=AppState.set_show_qr_display_modal,
    )

def post_admin_row(post: AdminPostRowData) -> rx.Component:
    """Componente para una fila de la tabla de administración."""
    return rx.table.row(
        rx.table.cell(
            rx.cond(
                post.main_image_url != "",
                rx.avatar(src=rx.get_upload_url(post.main_image_url), size="4"),
                rx.box(rx.icon("image_off", size=24), width="var(--avatar-size-4)", height="var(--avatar-size-4)", bg=rx.color("gray", 3), display="flex", align_items="center", justify_content="center", border_radius="100%")
            )
        ),
        rx.table.cell(
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
                rx.button("Editar", on_click=lambda: AppState.start_editing_post(post.id), variant="outline", size="2"),
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
        rx.table.cell(
            rx.icon_button(
                rx.icon("qr-code"),
                on_click=AppState.open_qr_modal(post.id),
                variant="soft",
                size="2"
            )
        ),
        align="center",
    )

def desktop_post_row(post: AdminPostRowData) -> rx.Component:
    """Componente para una fila de la tabla de administración en escritorio."""
    return rx.table.row(
        rx.table.cell(
            rx.cond(
                post.main_image_url != "",
                rx.avatar(src=rx.get_upload_url(post.main_image_url), size="4"),
                rx.box(rx.icon("image_off", size=24), width="var(--avatar-size-4)", height="var(--avatar-size-4)", bg=rx.color("gray", 3), display="flex", align_items="center", justify_content="center", border_radius="100%")
            )
        ),
        rx.table.cell(
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
                rx.button("Editar", on_click=lambda: AppState.start_editing_post(post.id), variant="outline", size="2"),
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
        rx.table.cell(
            rx.icon_button(
                rx.icon("qr-code"),
                on_click=AppState.open_qr_modal(post.id),
                variant="soft",
                size="2"
            )
        ),
        align="center",
    )

def mobile_post_card(post: AdminPostRowData) -> rx.Component:
    """Componente de tarjeta optimizado para la vista móvil."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.avatar(src=rx.get_upload_url(post.main_image_url), size="5", radius="medium"),
                rx.vstack(
                    rx.heading(post.title, size="4", trim="end", no_of_lines=1, width="150px"),
                    rx.text(post.price_cop, size="3", color_scheme="gray"),
                    align_items="start",
                    spacing="0",
                ),
                rx.spacer(),
                rx.icon_button(rx.icon("qr-code"), on_click=AppState.open_qr_modal(post.id)),
                align="center",
                width="100%",
            ),
            rx.divider(margin_y="0.75em"),
            rx.hstack(
                rx.text("Estado:", weight="medium", size="2"),
                rx.spacer(),
                rx.badge(
                    rx.cond(post.publish_active, "Visible", "Oculto"),
                    color_scheme=rx.cond(post.publish_active, "green", "gray"),
                ),
                rx.switch(
                    is_checked=post.publish_active,
                    on_change=lambda checked: AppState.toggle_publish_status(post.id),
                ),
                align="center",
                justify="end",
                spacing="3",
                width="100%",
            ),
            rx.hstack(
                rx.button("Editar", on_click=AppState.start_editing_post(post.id), width="100%", size="2"),
                rx.alert_dialog.root(
                    rx.alert_dialog.trigger(
                        rx.button("Eliminar", color_scheme="red", width="100%", size="2")
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
                width="100%",
                margin_top="0.5em",
            ),
            spacing="2",
            width="100%",
        )
    )


@require_admin
def blog_admin_page() -> rx.Component:
    """Página de 'Mis Publicaciones' para el vendedor, ahora completamente responsiva."""

    desktop_view = rx.box(
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
                rx.foreach(AppState.my_admin_posts, desktop_post_row)
            ),
            variant="surface", width="100%",
        ),
        display=["none", "none", "block", "block"],
    )

    mobile_view = rx.box(
        rx.vstack(
            rx.foreach(AppState.my_admin_posts, mobile_post_card),
            spacing="4",
            width="100%",
        ),
        display=["block", "block", "none", "none"],
    )

    return rx.center(
        rx.container(
            rx.vstack(
                rx.flex(
                    rx.heading("Mis Publicaciones", size={"initial": "8", "md": "7"}),
                    rx.spacer(),
                    rx.button(
                        "Crear Nueva Publicación", 
                        on_click=rx.redirect(navigation.routes.BLOG_POST_ADD_ROUTE), 
                        color_scheme="violet",
                        width={"initial": "100%", "md": "auto"},
                    ),
                    direction={"initial": "column", "md": "row"},
                    spacing="4",
                    align={"initial": "stretch", "md": "center"},
                    width="100%",
                ),
                
                rx.divider(margin_y="1.5em"),

                rx.cond(
                    AppState.my_admin_posts,
                    rx.fragment(desktop_view, mobile_view),
                    rx.center(rx.text("Aún no tienes publicaciones."), height="50vh")
                ),

                # --- INICIO DE LA CORRECCIÓN ---
                # Se eliminó el formulario de edición de aquí y en su lugar
                # se llaman a los componentes de los modales.
                edit_post_dialog(),
                qr_display_modal(),
                # --- FIN DE LA CORRECCIÓN ---
                
                spacing="5", 
                width="100%",
            ),
            max_width="1400px",
            width="100%",
            padding_y="2em",
        ),
        min_height="85vh",
        width="100%",
    )