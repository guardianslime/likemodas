# likemodas/account/saved_posts.py (NUEVO ARCHIVO)

import reflex as rx
import reflex_local_auth
from ..state import AppState
from ..account.layout import account_layout
from ..ui.components import product_gallery_component
from ..ui.skeletons import skeleton_product_gallery

@reflex_local_auth.require_login
def saved_posts_content() -> rx.Component:
    """Página que muestra las publicaciones guardadas por el usuario."""
    page_content = rx.vstack(
        rx.heading("Mis Publicaciones Guardadas", size="7"),
        rx.text("Aquí encontrarás los productos que has guardado para ver más tarde.", margin_bottom="1.5em"),
        rx.cond(
            AppState.is_loading,
            skeleton_product_gallery(),
            rx.cond(
                AppState.saved_posts_gallery,
                product_gallery_component(posts=AppState.saved_posts_gallery),
                rx.center(
                    rx.text("Aún no has guardado ninguna publicación."),
                    min_height="40vh"
                )
            )
        ),
        align_items="start", 
        width="100%",
    )
    return account_layout(page_content)