# likemodas/pages/processing_payment.py

import reflex as rx
from ..state import AppState
from ..ui.base import base_page

def processing_payment_page() -> rx.Component:
    """Página que se muestra mientras se sondea la URL de pago de Sistecredito."""
    return base_page(
        rx.center(
            rx.vstack(
                rx.heading("Procesando tu pago..."),
                rx.text(
                    "Estamos contactando a Sistecredito para generar tu enlace de pago.",
                    "Por favor, espera un momento, serás redirigido automáticamente.",
                    text_align="center"
                ),
                rx.spinner(size="3", margin_top="1.5em"),
                spacing="5",
                align="center"
            ),
            min_height="85vh"
        )
    )