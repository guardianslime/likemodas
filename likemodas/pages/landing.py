# likemodas/pages/landing.py (VERSIÓN FINAL Y CORRECTA)

import reflex as rx
from ..state import AppState

# Importamos las dos vistas que queremos mostrar condicionalmente
from ..admin.store_page import admin_store_page
from ..blog.public_page import blog_public_page_content

def landing_content() -> rx.Component:
    """
    Página de aterrizaje que muestra la vista correcta
    según el rol del usuario (Admin/Vendedor vs. Cliente).
    """
    return rx.box(
        rx.cond(
            # --- ¡CORRECCIÓN CLAVE! ---
            # Muestra el punto de venta si es Admin O Vendedor
            AppState.is_admin | AppState.is_vendedor,
            admin_store_page(),
            # Si no, muestra la galería pública
            blog_public_page_content()
        ),
        width="100%"
    )