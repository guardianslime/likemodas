# likemodas/components/base.py (CORREGIDO Y DEFINITIVO)

import reflex as rx
from .navbar import navbar
from reflex.components.sonner import Toaster # <--- 1. AÑADE ESTA IMPORTACIÓN DIRECTA

def base_page(child: rx.Component) -> rx.Component:
    """Un layout base que incluye la navbar y el contenedor de notificaciones."""
    return rx.box(
        navbar(),
        child,
        # ▼▼▼ 2. USA EL COMPONENTE IMPORTADO DIRECTAMENTE ▼▼▼
        Toaster(position="bottom-right", theme="dark"),
    )