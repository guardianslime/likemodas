# likemodas/pages/dashboard.py

import reflex as rx 
from ..ui.components import product_gallery_component
from ..cart.state import CartState

def dashboard_component() -> rx.Component:
    return rx.box(
        rx.heading("Bienvenido de regreso", size='2'),
        rx.divider(margin_top='1em', margin_bottom='1em'),
        # --- CORRECCIÓN AQUÍ: de CartState.posts a CartState.posts ---
        product_gallery_component(posts=CartState.posts[:20]),
        min_height="85vh",
    )