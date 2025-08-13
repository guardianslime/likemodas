# likemodas/blog/public_page.py (VERSIÓN FINAL Y CORREGIDA)

import reflex as rx
from ..state import AppState
from ..ui.components import product_gallery_component
from ..ui.filter_panel import floating_filter_panel
from ..ui.skeletons import skeleton_product_detail_view, skeleton_product_gallery

def product_detail_modal() -> rx.Component:
    """El diálogo modal que muestra los detalles del producto."""
    
    def _modal_image_section() -> rx.Component:
        FIXED_HEIGHT = "500px"
        return rx.box(
            rx.cond(
                AppState.product_in_modal.image_urls & (AppState.product_in_modal.image_urls.length() > 0),
                rx.fragment(
                    rx.image(
                        src=rx.get_upload_url(AppState.current_image_url),
                        alt=AppState.product_in_modal.title,
                        width="100%", height="100%", object_fit="cover",
                    ),
                    rx.button(rx.icon(tag="chevron-left"), on_click=AppState.prev_image, position="absolute", top="50%", left="0.5rem", variant="soft"),
                    rx.button(rx.icon(tag="chevron-right"), on_click=AppState.next_image, position="absolute", top="50%", right="0.5rem", variant="soft"),
                ),
                rx.box(rx.icon("image_off", size=48), width="100%", height="100%", bg=rx.color("gray", 3), display="flex", align_items="center", justify_content="center"),
            ),
            position="relative", width="100%", height=FIXED_HEIGHT, border_radius="var(--radius-3)", overflow="hidden",
        )

    def _modal_info_section() -> rx.Component:
        return rx.vstack(
            rx.text(AppState.product_in_modal.title, size="8", font_weight="bold", text_align="left"),
            rx.text("Publicado el " + AppState.product_in_modal.created_at_formatted, size="3", color_scheme="gray", text_align="left"),
            rx.text(AppState.product_in_modal.price_cop, size="7", color_scheme="gray", text_align="left"),
            rx.text(AppState.product_in_modal.content, size="4", margin_top="1em", white_space="pre-wrap", text_align="left"),
            rx.spacer(),
            rx.button(
                "Añadir al Carrito",
                on_click=AppState.add_to_cart(AppState.product_in_modal.id),
                width="100%", size="3", margin_top="1.5em",
            ),
            align="start",
            height="100%",
        )

    return rx.dialog.root(
        rx.dialog.content(
            # --- CORRECCIÓN DEFINITIVA AQUÍ ---
            # Los componentes hijos van primero
            rx.dialog.close(
                rx.icon_button(
                    rx.icon("x"), 
                    variant="soft", 
                    color_scheme="gray", 
                    style={"position": "absolute", "top": "1rem", "right": "1rem"}
                )
            ),
            rx.cond(
                AppState.product_in_modal,
                rx.grid(
                    _modal_image_section(),
                    _modal_info_section(),
                    columns={"initial": "1", "md": "2"},
                    spacing="6",
                    align_items="start",
                    width="100%",
                ),
                skeleton_product_detail_view(),
            ),
            # El argumento de palabra clave `style` va al final
            style={"max_width": "1200px", "min_height": "600px"},
        ),
        open=AppState.show_detail_modal,
        on_open_change=AppState.close_product_detail_modal,
    )

def blog_public_page_content() -> rx.Component:
    """Página pública principal que muestra la galería y contiene el modal."""
    return rx.center(
        rx.vstack(
            floating_filter_panel(),
            rx.cond(
                AppState.is_loading,
                skeleton_product_gallery(),
                product_gallery_component(posts=AppState.posts)
            ),
            product_detail_modal(),
            spacing="6", width="100%", padding="2em", align="center"
        ),
        width="100%"
    )
