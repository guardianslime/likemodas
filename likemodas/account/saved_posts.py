# likemodas/account/saved_posts.py (VERSIÓN FINAL)

import reflex as rx
import reflex_local_auth
from ..state import AppState
from ..account.layout import account_layout
from ..ui.components import product_gallery_component
from ..ui.skeletons import skeleton_product_gallery
from ..blog.public_page import product_detail_modal

@reflex_local_auth.require_login
def saved_posts_page() -> rx.Component:
    """Página que muestra las publicaciones guardadas por el usuario."""
    # --- INICIO DE LA CORRECCIÓN DE LAYOUT ---
    page_content = rx.vstack(
        rx.heading("Mis Publicaciones Guardadas", size="8", text_align="center"),
        rx.text("Aquí encontrarás los productos que has guardado para ver más tarde.", margin_bottom="1.5em", color_scheme="gray", size="4", text_align="center"),
        rx.divider(margin_y="1.5em"),
        rx.cond(
            AppState.is_loading,
            skeleton_product_gallery(),
            rx.cond(
                AppState.saved_posts_gallery,
                product_gallery_component(posts=AppState.saved_posts_gallery),
                rx.center(
                    rx.vstack(
                        rx.icon("bookmark-x", size=48, color_scheme="gray"),
                        rx.text("Aún no has guardado ninguna publicación."),
                        spacing="4"
                    ),
                    padding_y="5em",
                )
            )
        ),
        align="center",
        width="100%",
        max_width="1600px" # Ancho máximo para la galería
    )
    # --- FIN DE LA CORRECCIÓN DE LAYOUT ---
    
    return rx.fragment(
        account_layout(page_content),
        product_detail_modal(),
    )