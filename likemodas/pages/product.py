# likemodas/pages/product.py (CORREGIDO)

import reflex as rx
from likemodas.state import ProductDetailState

def skeleton_loader() -> rx.Component:
    # ... (el código del esqueleto no cambia) ...
    return rx.grid(
        rx.box(height="400px", background_color=rx.color("gray", 4), border_radius="md"),
        rx.vstack(
            rx.box(height="38px", width="80%", background_color=rx.color("gray", 4), border_radius="md"),
            rx.box(height="28px", width="40%", background_color=rx.color("gray", 4), border_radius="md", margin_top="1em"),
            rx.box(height="105px", width="100%", background_color=rx.color("gray", 4), border_radius="md", margin_top="1em"),
            rx.spacer(),
            rx.box(height="40px", width="100%", background_color=rx.color("gray", 4), border_radius="md", margin_top="1em"),
            align="start", height="100%", width="100%",
        ),
        columns={"initial": "1", "md": "2"}, spacing="6", width="100%",
    )

def product_page() -> rx.Component:
    """Página de detalle con manejo de hidratación para evitar errores."""
    return rx.container(
        rx.cond(
            ProductDetailState.is_hydrated,
            rx.grid(
                rx.image(src=rx.get_upload_url(ProductDetailState.product_detail.image_urls[0]), width="100%", height="auto", border_radius="md"),
                rx.vstack(
                    rx.heading(ProductDetailState.product_detail.title, size="8"),
                    rx.text(f"${ProductDetailState.product_detail.price:.0f} COP", size="6", color_scheme="gray", margin_y="1em"),
                    rx.text(ProductDetailState.product_detail.content, white_space="pre-wrap"),
                    rx.spacer(),
                    rx.button(
                        "Añadir al Carrito",
                        on_click=lambda: ProductDetailState.add_to_cart(ProductDetailState.product_detail.id),
                        width="100%", size="3", margin_top="1em",
                        is_disabled=ProductDetailState.is_loading | (ProductDetailState.product_detail.is_none()),
                    ),
                    align="start", height="100%",
                ),
                columns={"initial": "1", "md": "2"}, spacing="6", width="100%",
            ),
            skeleton_loader(),
        ),
        padding_top="8em",
        # ▼▼▼ on_mount AHORA ESTÁ AQUÍ, EN EL COMPONENTE RAÍZ DE LA PÁGINA ▼▼▼
        on_mount=ProductDetailState.set_hydrated,
    )