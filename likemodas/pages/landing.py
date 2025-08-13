# likemodas/pages/landing.py (VERSIÓN FINAL Y CORRECTA)

import reflex as rx
from ..state import AppState

# Importamos las dos vistas que queremos mostrar condicionalmente
from ..admin.store_page import admin_store_page
from ..blog.public_page import blog_public_page_content

def landing_content() -> rx.Component:
    """
    Página de aterrizaje inteligente que muestra la vista correcta
    según si el usuario es administrador o no.
    """
    return rx.box(
        rx.cond(
            AppState.is_admin,
            # Si es admin, muestra la página de la tienda de administración
            admin_store_page(),
            # Si no, muestra la galería pública con sus modales
            blog_public_page_content()
        ),
        width="100%"
    )