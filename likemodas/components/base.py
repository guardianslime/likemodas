# likemodas/components/base.py (CORREGIDO Y SIMPLIFICADO)

import reflex as rx
from .navbar import navbar

def base_page(child: rx.Component) -> rx.Component:
    """Un layout base que solo incluye la navbar."""
    return rx.box(
        navbar(),
        child,
        # La línea del toaster/toast se ha eliminado por completo.
    )