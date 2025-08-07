# likemodas/components/navbar.py

import reflex as rx
from likemodas.state import AppState

def navbar() -> rx.Component:
    """La barra de navegación principal."""
    return rx.box(
        rx.hstack(
            rx.link(
                rx.image(src="/logo.png", width="8em", height="auto"),
                href="/"
            ),
            rx.spacer(),
            rx.link("Admin", href="/admin", button=True, variant="outline"),
            rx.link(
                rx.hstack(
                    rx.icon("shopping-cart"),
                    rx.badge(
                        AppState.cart_items_count,
                        variant="solid",
                        color_scheme="red",
                    ),
                    spacing="3"
                ),
                href="/cart", # Aunque no creemos la página del carrito, el enlace puede existir
            ),
            align="center",
            width="100%",
        ),
        position="fixed",
        top="0",
        left="0",
        right="0",
        padding="1em",
        bg=rx.color("gray", 2),
        z_index="1000",
        width="100%",
    )