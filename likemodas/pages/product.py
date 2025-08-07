# likemodas/pages/product.py (SOLUCIÓN DEFINITIVA)

import reflex as rx
from likemodas.state import ProductDetailState # <--- Importamos el nuevo estado

def skeleton_loader() -> rx.Component:
    """Muestra un esqueleto de carga que ocupa el mismo espacio que el contenido real."""
    return rx.grid(
        # Columna de la imagen esqueleto
        rx.box(height="400px", background_color=rx.color("gray", 4), border_radius="md"),
        # Columna de la info esqueleto
        rx.vstack(
            rx.box(height="36px", width="80%", background_color=rx.color("gray", 4), border_radius="md"),
            rx.box(height="24px", width="40%", background_color=rx.color("gray", 4), border_radius="md", margin_top="1em"),
            rx.box(height="80px", width="100%", background_color=rx.color("gray", 4), border_radius="md", margin_top="1em"),
            rx.spacer(),
            # ✨ EXPLICACIÓN: Este es el placeholder del botón. Ocupa el mismo espacio.
            rx.box(height="40px", width="100%", background_color=rx.color("gray", 4), border_radius="md", margin_top="1em"),
            align="start",
            height="100%",
            width="100%",
        ),
        columns={"initial": "1", "md": "2"},
        spacing="6",
        width="100%",
    )


def product_page() -> rx.Component:
    """Página de detalle que usa el estado de carga y el esqueleto."""
    return rx.container(
        # ✨ EXPLICACIÓN: La condición ahora se basa en el estado de carga, no en si el producto existe.
        rx.cond(
            ProductDetailState.is_loading,
            # Si está cargando, muestra el esqueleto
            skeleton_loader(),
            # Si no, muestra el contenido real
            rx.grid(
                rx.vstack(
                    rx.image(
                        src=rx.get_upload_url(ProductDetailState.product_detail.image_urls[0]),
                        width="100%", height="auto", border_radius="md",
                    ),
                    align="center",
                ),
                rx.vstack(
                    rx.heading(ProductDetailState.product_detail.title, size="8"),
                    rx.text(f"${ProductDetailState.product_detail.price:.0f} COP", size="6", color_scheme="gray", margin_y="0.5em"),
                    rx.text(ProductDetailState.product_detail.content, white_space="pre-wrap"),
                    rx.spacer(),
                    rx.button(
                        "Añadir al Carrito",
                        on_click=lambda: ProductDetailState.add_to_cart(ProductDetailState.product_detail.id),
                        width="100%", size="3", margin_top="1em", height="40px", # <-- Altura fija
                    ),
                    align="start", height="100%",
                ),
                columns={"initial": "1", "md": "2"},
                spacing="6", width="100%",
            ),
        ),
        padding_top="8em",
    )