# likemodas/account/shipping_info.py

import reflex as rx
import reflex_local_auth
from ..ui.base import base_page
from .layout import account_layout
from ..cart.page import checkout_form # Reutilizamos el formulario

@reflex_local_auth.require_login
def shipping_info_page() -> rx.Component:
    """Página para mostrar el formulario de información de envío."""
    return base_page(
        account_layout(
            rx.vstack(
                rx.heading("Mi Información para Envíos", size="7"),
                rx.text(
                    "Aquí puedes gestionar tu información de envío predeterminada.",
                    margin_bottom="1.5em"
                ),
                checkout_form(), # Usamos el mismo formulario
                align_items="start",
                width="100%",
                max_width="700px"
            )
        )
    )