# likemodas/account/layout.py

import reflex as rx
from .sidebar import account_sidebar
# ✅ Se importa SessionState para verificar la hidratación
from ..auth.state import SessionState

def account_layout(child: rx.Component) -> rx.Component:
    """
    Layout que envuelve las páginas de la sección Mi Cuenta,
    ahora con un patrón de carga seguro que espera la hidratación del estado.
    """
    # 🛡️ Se añade el condicional para esperar la hidratación
    return rx.cond(
        ~SessionState.is_hydrated,
        
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