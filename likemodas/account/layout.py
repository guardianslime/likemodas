# likemodas/account/layout.py (CORREGIDO)

import reflex as rx
from .sidebar import account_sidebar
from ..state import AppState

def account_layout(child: rx.Component) -> rx.Component:
    """Layout que envuelve las páginas de la sección Mi Cuenta."""
    return rx.cond(
        (AppState.is_hydrated == False), # ✅ CORRECTO
        # Muestra un spinner si el estado no está listo
        rx.center(rx.spinner(size="3"), height="85vh"),
        
        # Muestra el contenido solo cuando el estado está hidratado
        rx.hstack(
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
    )
