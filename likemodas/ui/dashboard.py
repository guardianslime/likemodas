# likemodas/pages/dashboard.py (VERSIÓN CORREGIDA)

import reflex as rx 
from ..blog.page import product_gallery_component
from ..cart.state import CartState

def dashboard_component() -> rx.Component:
    return rx.box(
        rx.heading("Bienvenido de regreso", size='2'),
        rx.divider(margin_top='1em', margin_bottom='1em'),
        # ✨ CAMBIO: Se usa el nuevo componente y se le pasa una porción de la lista de posts
        product_gallery_component(posts=CartState.posts[:20]),
        min_height="85vh",
    )