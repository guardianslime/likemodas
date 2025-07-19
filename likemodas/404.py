# likemodas/404.py

import reflex as rx
from .ui.base import base_page

# Reflex encontrará automáticamente esta función y la usará como la página 404.
def four_oh_four():
    """La página personalizada para errores 404 (Página No Encontrada)."""
    return base_page(
        rx.vstack(
            rx.heading("404", size="9"),
            rx.text("Lo sentimos, la página que buscas no existe."),
            rx.link(
                "Volver al Inicio",
                href="/",
                button=True,
                color_scheme="gray",
            ),
            spacing="5",
            justify="center",
            align="center",
            min_height="85vh",
        )
    )