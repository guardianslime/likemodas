# likemodas/components/base.py (CORREGIDO)

import reflex as rx
from .navbar import navbar

def base_page(child: rx.Component) -> rx.Component:
    """Un layout base que incluye la navbar y el contenedor de notificaciones."""
    return rx.box(
        navbar(),
        child,
        # ▼▼▼ ESTA ES LA LÍNEA CORREGIDA Y DEFINITIVA ▼▼▼
        # El alias correcto es rx.toaster (todo en minúscula)
        rx.toaster(position="bottom-right", theme="dark"),
    )