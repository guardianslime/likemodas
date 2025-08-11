# likemodas/admin/store_page.py

import reflex as rx
# --- RUTAS CORREGIDAS PARA LA NUEVA UBICACIÓN ---
from ..auth.admin_auth import require_admin
from ..state import AppState
# Importa desde el archivo hermano, no de una subcarpeta.
from .store_components import admin_store_gallery_component

@require_admin
def admin_store_page() -> rx.Component:
    """Página principal de la tienda para administradores."""
    return rx.vstack(
        rx.heading("Tienda (Vista de Administrador)", size="8"),
        rx.text("Aquí puedes ver todos los productos publicados y acceder a su edición."),
        rx.divider(margin_y="1.5em"),
        rx.cond(
            AppState.admin_store_posts,
            admin_store_gallery_component(posts=AppState.admin_store_posts),
            rx.center(
                rx.text("No hay productos para mostrar."),
                padding="4em"
            )
        ),
        spacing="5",
        padding="2em",
        width="100%",
        align="center",
    )
