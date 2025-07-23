# likemodas/blog/page.py

import reflex as rx
from ..ui.base import base_page 
from ..cart.state import CartState 
from ..ui.gallery_header import gallery_header
from ..ui.filter_sidebar import floating_filter_sidebar 
# --- 👇 IMPORTA EL COMPONENTE CORRECTO 👇 ---
from ..ui.components import product_gallery_component

def blog_public_page():
    """Página principal que ahora usa los componentes correctos y reutilizables."""
    return base_page(
        floating_filter_sidebar(),
        rx.center(
            rx.vstack(
                gallery_header(),
                product_gallery_component(posts=CartState.filtered_posts),
                spacing="6", 
                width="100%", 
                padding="2em", 
                align="center",
                transition="padding-left 0.3s ease",
                padding_left=rx.cond(
                    CartState.show_filters, "220px", "0px"
                ),
            ),
            width="100%",
        )
    )