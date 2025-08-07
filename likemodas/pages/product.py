# likemodas/pages/product.py

import reflex as rx
from likemodas.state import ProductDetailState

def info_section_skeleton() -> rx.Component:
    return rx.vstack(
        rx.box(height="38px", width="80%", background_color=rx.color("gray", 4), border_radius="md"),
        rx.box(height="28px", width="40%", background_color=rx.color("gray", 4), margin_y="1em", border_radius="md"),
        rx.box(height="105px", width="100%", background_color=rx.color("gray", 4), border_radius="md"),
        rx.spacer(),
        rx.box(height="40px", width="100%", background_color=rx.color("gray", 4), margin_top="1em", border_radius="md"),
        align="start", height="100%", width="100%",
    )

def product_page() -> rx.Component:
    return rx.container(
        rx.grid(
            rx.image(
                src=rx.get_upload_url(ProductDetailState.product_detail.image_urls[0]),
                width="100%", height="auto", border_radius="md",
                fallback=rx.box(height="400px", width="100%", background_color=rx.color("gray", 4), border_radius="md"),
            ),
            rx.cond(
                ProductDetailState.is_hydrated,
                rx.vstack(
                    rx.heading(ProductDetailState.product_detail.title, size="8"),
                    rx.text(f"${ProductDetailState.product_detail.price:.0f} COP", size="6", color_scheme="gray", margin_y="1em"),
                    rx.text(ProductDetailState.product_detail.content, white_space="pre-wrap"),
                    rx.spacer(),
                    rx.button(
                        "Añadir al Carrito",
                        on_click=lambda: ProductDetailState.add_to_cart(ProductDetailState.product_detail.id),
                        width="100%", size="3", margin_top="1em",
                        is_disabled=ProductDetailState.product_detail.is_none(),
                    ),
                    align="start", height="100%",
                ),
                info_section_skeleton(),
            ),
            columns={"initial": "1", "md": "2"}, spacing="6", width="100%",
        ),
        on_mount=ProductDetailState.set_is_hydrated(True),
        padding_top="8em",
    )