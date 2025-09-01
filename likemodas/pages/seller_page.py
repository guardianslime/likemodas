# likemodas/pages/seller_page.py

import reflex as rx
from ..state import AppState
from ..ui.components import product_gallery_component
from ..ui.skeletons import skeleton_product_gallery
from ..blog.public_page import product_detail_modal

def seller_page_content() -> rx.Component:
    """Página pública que muestra todos los productos de un vendedor específico."""
    return rx.center(
        rx.vstack(
            rx.cond(
                AppState.seller_page_info,
                rx.heading(
                    "Publicaciones de ",
                    rx.text(
                        # --- 👇 LÍNEA CORREGIDA 👇 ---
                        # Se accede a .username directamente desde el nuevo modelo de datos.
                        AppState.seller_page_info.username,
                        as_="span",
                        color_scheme="violet",
                    ),
                    size="8"
                ),
                rx.heading("Cargando vendedor...", size="8")
            ),
            rx.divider(margin_y="1.5em"),
            rx.cond(
                AppState.is_loading,
                skeleton_product_gallery(),
                rx.cond(
                    AppState.seller_page_posts,
                    product_gallery_component(posts=AppState.seller_page_posts),
                    rx.center(
                        rx.text("Este vendedor aún no tiene publicaciones activas."),
                        min_height="40vh"
                    )
                )
            ),
            
            product_detail_modal(),

            spacing="6", width="100%", padding="2em", align="center"
        ),
        width="100%"
    )

