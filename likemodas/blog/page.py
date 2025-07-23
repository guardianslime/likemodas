# likemodas/blog/page.py (VERSIÓN REFACTORIZADA)

import reflex as rx
from ..ui.base import base_page 
from ..cart.state import CartState 
from ..navigation import routes
import math
from ..models import BlogPostModel
from ..ui.components import product_gallery_component
from ..ui.gallery_header import gallery_header
from ..ui.filter_sidebar import floating_filter_sidebar 

# --- ✨ PÁGINA SIMPLIFICADA USANDO EL NUEVO COMPONENTE --- ✨
def blog_public_page():
    return base_page(
        # --- 👇 AÑADE EL COMPONENTE FLOTANTE AQUÍ 👇 ---
        floating_filter_sidebar(),
        rx.center(
            rx.vstack(
                gallery_header(),
                product_gallery_component(posts=CartState.filtered_posts), 
                spacing="6", 
                width="100%", 
                padding="2em", 
                align="center",
                # --- Propiedades para el desplazamiento suave ---
                transition="padding-left 0.3s ease",
                padding_left=rx.cond(
                    CartState.show_filters, "220px", "0px"
                ),
            ),
        )
    )