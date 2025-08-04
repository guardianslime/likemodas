# likemodas/pages/search_results.py (VERSIÓN FINAL Y CORREGIDA)

import reflex as rx
from ..ui.search_state import SearchState
from ..ui.components import product_gallery_component

def search_results_content() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading(f"Resultados para: '{SearchState.search_term}'", size="7"),
            rx.cond(
                SearchState.search_results,
                product_gallery_component(posts=SearchState.search_results),
                rx.center(
                    rx.text(f"😔 No se encontraron publicaciones con el nombre: '{SearchState.search_term}'"),
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