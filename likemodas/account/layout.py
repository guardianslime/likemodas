# likemodas/account/layout.py (CORREGIDO)

import reflex as rx
from .sidebar import account_sidebar
from ..state import AppState

def account_layout(child: rx.Component) -> rx.Component:
    """Layout que envuelve las páginas de la sección Mi Cuenta."""
    return rx.cond(
        ~AppState.is_hydrated,
        # ... (spinner sin cambios) ...
        rx.hstack(
            account_sidebar(),
            rx.box(
                child,
                
                # --- INICIO DE LA CORRECCIÓN ---
                # Antes: padding="2em"
                # Ahora, especificamos más padding horizontal (eje X)
                padding_x="4em", 
                padding_y="2em",
                # --- FIN DE LA CORRECCIÓN ---

                width="100%",
            ),
            align_items="start",
            min_height="85vh",
            width="100%"
        )
    )
