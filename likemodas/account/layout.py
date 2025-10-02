# likemodas/account/layout.py (CORREGIDO)

import reflex as rx
from .sidebar import account_sidebar
from ..state import AppState
from ..ui.base import base_page  # <-- IMPORTANTE: Importamos el layout base

def account_layout(child: rx.Component) -> rx.Component:
    """
    Layout corregido que envuelve las páginas de la sección Mi Cuenta.
    Ahora usa 'base_page' para incluir la barra de navegación principal.
    """
    # El contenido de la cuenta es un Hstack con el sidebar y la página hija
    account_content = rx.hstack(
        account_sidebar(),
        rx.box(
            child,
            padding="2em",
            width="100%",
        ),
        align_items="start",
        min_height="85vh",
        width="100%"
    )

    # Envolvemos TODO en el base_page para obtener la navbar y la estructura principal
    return base_page(account_content)