# likemodas/pages/seller_page.py (Archivo Corregido)

import reflex as rx
from ..state import AppState
from ..ui.components import product_gallery_component
from ..ui.skeletons import skeleton_product_gallery
from ..blog.public_page import product_detail_modal

def seller_page_content() -> rx.Component:
    """Página pública que muestra todos los productos de un vendedor específico."""
    return rx.center(
        rx.vstack(
            # --- INICIO DE LA CORRECCIÓN ---
            # En lugar de asumir que seller_page_info existe, lo comprobamos con rx.cond.
            # Además, verificamos que el atributo 'user' dentro de 'seller_page_info' no sea nulo.
            rx.cond(
                (AppState.seller_page_info) & (AppState.seller_page_info.user),
                rx.heading(
                    "Publicaciones de ",
                    rx.text(
                        AppState.seller_page_info.user.username,
                        as_="span",
                        color_scheme="violet",
                    ),
                    size="8"
                ),
                # Muestra un texto de carga mientras se obtienen los datos.
                rx.heading("Cargando vendedor...", size="8")
            ),
            # --- FIN DE LA CORRECCIÓN ---
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