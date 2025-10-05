# likemodas/account/layout.py (CORREGIDO)

import reflex as rx
from .sidebar import account_sidebar
from ..state import AppState
from ..ui.base import base_page  # <-- IMPORTANTE: Importamos el layout base

def account_layout(child: rx.Component) -> rx.Component:
    """
    Layout corregido que envuelve las páginas de la sección Mi Cuenta.
    [cite_start]Ahora usa 'base_page' para incluir la barra de navegación principal[cite: 2064, 2135].
    """
    # [cite_start]El contenido de la cuenta es un Hstack con el sidebar y la página hija [cite: 2075]
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

    # [cite_start]Envolvemos TODO en el base_page para obtener la navbar y la estructura principal [cite: 49, 2078]
    return base_page(account_content)