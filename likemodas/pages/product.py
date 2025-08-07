# likemodas/pages/product.py (CORREGIDO)

import reflex as rx
from likemodas.state import AppState
# Se elimina la importación de la navbar de aquí

def product_page() -> rx.Component:
    """Página de detalle para un producto específico."""
    # Ya no se necesita el rx.box exterior
    return rx.cond(
        AppState.product_detail,
        rx.container(
            rx.grid(
                rx.vstack(
                    rx.image(
                        src=rx.get_upload_url(AppState.product_detail.image_urls[0]),
                        width="100%",
                        height="auto",
                        border_radius="md",
                    ),
                    align="center",
                ),
                rx.vstack(
                    rx.heading(AppState.product_detail.title, size="8"),
                    rx.text(
                        f"${AppState.product_detail.price:.0f} COP",
                        size="6",
                        color_scheme="gray",
                        margin_y="0.5em"
                    ),
                    rx.text(AppState.product_detail.content, white_space="pre-wrap"),
                    rx.spacer(),
                    rx.button(
                        "Añadir al Carrito",
                        on_click=lambda: AppState.add_to_cart(AppState.product_detail.id),
                        width="100%",
                        size="3",
                        margin_top="1em",
                    ),
                    align="start",
                    height="100%",
                ),
                columns=["1", "1", "1", "2"],
                spacing="6",
                width="100%",
            ),
            padding_top="8em",
        ),
        rx.center(rx.circular_progress(is_indeterminate=True), padding_top="10em")
    )