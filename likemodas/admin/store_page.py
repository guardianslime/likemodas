# likemodas/admin/store_page.py (CORREGIDO)

import reflex as rx
from ..auth.admin_auth import require_admin
from ..state import AppState
from .store_components import admin_store_gallery_component

# --- ✨ 1. IMPORTAMOS EL DIÁLOGO MODAL QUE YA FUNCIONA EN /blog ---
from ..blog.admin_page import edit_post_dialog

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
        
        # --- ✨ 2. AÑADIMOS EL COMPONENTE DEL MODAL A LA PÁGINA ---
        # Ahora, cuando el botón cambie el estado `is_editing_post`,
        # este componente reaccionará y se mostrará.
        edit_post_dialog(),
        
        spacing="5",
        padding="2em",
        width="100%",
        align="center",
    )