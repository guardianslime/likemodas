# likemodas/pages/dashboard.py (CORREGIDO)

import reflex as rx 
from ..ui.components import product_gallery_component
from ..state import AppState

def dashboard_content() -> rx.Component:
    return rx.box(
        rx.heading("Bienvenido de regreso", size='2'),
        rx.divider(margin_top='1em', margin_bottom='1em'),
        # ✨ CAMBIO: Se usa AppState y se le pasa una porción de la lista de posts
        product_gallery_component(posts=AppState.posts[:12]),
        min_height="85vh",
    )

