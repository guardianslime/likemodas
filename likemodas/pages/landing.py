# likemodas/pages/landing.py

import reflex as rx 
from .. import navigation
from ..ui.components import product_gallery_component
from ..cart.state import CartState

def landing_component() -> rx.Component:
    return rx.vstack(
        rx.heading("Bienvenidos a Likemodas", size="9"),
        rx.link(
            rx.button("About us", color_scheme='gray'),
            href=navigation.routes.ABOUT_US_ROUTE
        ),
        rx.divider(),
        rx.heading("Publicaciones Recientes", size="5"),
        # --- CORRECCIÓN AQUÍ: de CartState.posts a cart_state.posts ---
        product_gallery_component(posts=CartState.posts[:1]),
        spacing="5",
        justify="center",
        align="center",
        min_height="85vh",
        id="my-child"
    )