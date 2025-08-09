import reflex as rx
from ..state import AppState
from ..ui.components import product_gallery_component
from ..ui.filter_panel import floating_filter_panel

def blog_public_page_content() -> rx.Component:
    """Página pública que ahora es la principal y muestra la galería."""
    return rx.center(
        rx.vstack(
            rx.cond(
                AppState.is_hydrated,
                rx.cond(
                    ~AppState.is_admin,
                    floating_filter_panel()
                )
            ),
            # Usamos la lista completa de posts públicos desde el AppState
            product_gallery_component(posts=AppState.posts), 
            spacing="6", 
            width="100%", 
            padding="2em", 
            align="center"
        ),
        width="100%"
    )