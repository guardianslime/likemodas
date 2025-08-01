# likemodas/pages/dashboard.py (VERSIÓN CORREGIDA)

import reflex as rx 
from ..ui.components import product_gallery_component
from ..cart.state import CartState

def dashboard_component() -> rx.Component:
    return rx.box(
        rx.heading("Bienvenido de regreso", size='2'),
        rx.divider(margin_top='1em', margin_bottom='1em'),
        # ✅ SE USA LA NUEVA PROPIEDAD COMPUTADA
        product_gallery_component(posts=CartState.dashboard_posts),
        min_height="85vh",
    )