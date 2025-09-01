# likemodas/pages/dashboard.py (CORREGIDO)

import reflex as rx
from ..ui.components import product_gallery_component
from ..state import AppState

def dashboard_content() -> rx.Component:
    """El dashboard principal, ahora usa AppState."""
    return rx.box(
        rx.heading("Bienvenido de regreso", size='2'),
        rx.divider(margin_top='1em', margin_bottom='1em'),
        # Se usa el AppState centralizado para obtener los posts
        product_gallery_component(posts=AppState.posts[:20]),
        min_height="85vh",
    )

