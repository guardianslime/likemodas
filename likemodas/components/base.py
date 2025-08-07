# likemodas/components/base.py

import reflex as rx
from .navbar import navbar

def base_page(child: rx.Component) -> rx.Component:
    """Un layout base que incluye la navbar y las notificaciones toast."""
    return rx.box(
        navbar(),
        child,  # Aquí se renderizará el contenido de cada página
        rx.toast(position="bottom-right", theme="dark"),
    )