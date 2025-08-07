# likemodas/pages/product.py

import reflex as rx
from likemodas.state import AppState
from likemodas.components.navbar import navbar

def product_page() -> rx.Component:
    """Página de detalle para un producto específico."""
    return rx.box(
        navbar(),
        # Condición para mostrar contenido solo si el producto se ha cargado
        rx.cond(
            AppState.product_detail,
            rx.container(
                rx.grid(
                    # Columna de la imagen
                    rx.vstack(
                        rx.image(
                            src=rx.get_upload_url(AppState.product_detail.image_urls[0]),
                            width="100%",
                            height="auto",
                            border_radius="md",
                        ),
                        align="center",
                    ),
                    # Columna de la información y botón
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
            # Mensaje de carga mientras se obtienen los datos
            rx.center(rx.circular_progress(is_indeterminate=True), padding_top="10em")
        )
    )