# likemodas/pages/product.py (CORREGIDO)

import reflex as rx
from likemodas.state import AppState

def product_page() -> rx.Component:
    """Página de detalle para un producto específico."""
    return rx.cond(
        AppState.product_detail,
        rx.container(
            rx.grid(
                # Columna de la imagen (sin cambios)
                rx.vstack(
                    rx.image(
                        src=rx.get_upload_url(AppState.product_detail.image_urls[0]),
                        width="100%",
                        height="auto",
                        border_radius="md",
                    ),
                    align="center",
                ),
                # Columna de la información (sin cambios)
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
                # ▼▼▼ ESTA ES LA LÍNEA CORREGIDA ▼▼▼
                columns={
                    "initial": "1", # 1 columna en móvil
                    "md": "2",      # 2 columnas en tablets y escritorios
                },
                spacing="6",
                width="100%",
            ),
            padding_top="8em",
        ),
        rx.center(rx.spinner(size="3"), padding_top="10em")
    )