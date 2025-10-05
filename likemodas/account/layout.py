# likemodas/account/layout.py (CORREGIDO)

import reflex as rx
from .sidebar import account_sidebar
from ..ui.base import base_page

def account_layout(child: rx.Component) -> rx.Component:
    """
    Layout corregido que envuelve las páginas de la sección Mi Cuenta.
    Ahora centra el contenido de la página horizontalmente.
    """
    account_content = rx.hstack(
        account_sidebar(),
        # --- ✨ INICIO DE LA CORRECCIÓN CLAVE ✨ ---
        # Cambiamos rx.box por rx.vstack y añadimos align="center"
        # para que el contenido de la página (el 'child') se centre.
        rx.vstack(
            child,
            padding="2em",
            width="100%",
            align="center", # <-- Esta línea centra el contenido
        ),
        # --- ✨ FIN DE LA CORRECCIÓN CLAVE ✨ ---
        align_items="start",
        min_height="85vh",
        width="100%"
    )

    return base_page(account_content)