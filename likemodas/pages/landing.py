# likemodas/pages/landing.py (CORREGIDO Y COMPLETO)

import reflex as rx 
from .. import navigation
from ..ui.components import product_gallery_component
from ..state import AppState

def landing_content() -> rx.Component:
    """La página de inicio, ahora usa AppState y muestra las publicaciones recientes."""
    return rx.vstack(
        rx.heading("Bienvenidos a Likemodas", size="9"),
        rx.link(
            rx.button("Conócenos", color_scheme='gray'),
            href=navigation.routes.ABOUT_US_ROUTE
        ),
        rx.divider(),
        rx.heading("Publicaciones Recientes", size="5"),
        
        # CAMBIO CLAVE: Se usa AppState y se le pasa una porción de la lista de posts.
        # Se asume que los primeros 8 son los más recientes.
        product_gallery_component(posts=AppState.posts[:8]),
        
        spacing="5",
        justify="center",
        align="center",
        min_height="85vh",
    )