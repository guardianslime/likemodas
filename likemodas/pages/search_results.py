# likemodas/pages/search_results.py (CORREGIDO)

import reflex as rx
from ..state import AppState
from ..ui.components import product_gallery_component

def search_results_content() -> rx.Component:
    """Página de resultados de búsqueda, ahora usando AppState."""
    return rx.center(
        rx.vstack(
            rx.heading(f"Resultados para: '{AppState.search_term}'", size="7"),
            rx.cond(
                AppState.search_results,
                product_gallery_component(posts=AppState.search_results),
                rx.center(
                    rx.text(f"😔 No se encontraron publicaciones con el nombre: '{AppState.search_term}'"),
                    padding="4em",
                    min_height="40vh"
                )
            ),
            spacing="6",
            width="100%",
            padding="2em",
            align="center"
        ),
        width="100%"
    )
