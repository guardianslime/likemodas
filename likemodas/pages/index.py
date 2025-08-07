# likemodas/pages/index.py

import reflex as rx
from likemodas.state import AppState
from likemodas.components.navbar import navbar

def product_card(product: rx.Var[dict]) -> rx.Component:
    """Tarjeta para mostrar un producto en la galería."""
    return rx.link(
        rx.card(
            rx.inset(
                # Usamos rx.get_upload_url para obtener la URL de la imagen desde el backend
                rx.image(
                    src=rx.get_upload_url(product["image_urls"][0]),
                    width="100%",
                    height="250px",
                    object_fit="cover",
                ),
                pb="sm"
            ),
            rx.vstack(
                rx.text(product["title"], weight="bold"),
                rx.text(f"${product['price']:.0f} COP"),
                align="start",
            ),
        ),
        href=f"/product/{product['id']}",
    )

def index_page() -> rx.Component:
    """La página de inicio que muestra la galería de productos."""
    return rx.box(
        navbar(),
        rx.container(
            rx.heading("Nuestros Productos", size="8", margin_top="3em", margin_bottom="1em"),
            rx.grid(
                rx.foreach(AppState.products, product_card),
                columns=["1", "2", "3", "4"],
                spacing="4",
                width="100%",
            ),
            padding_top="5em",
        )
    )