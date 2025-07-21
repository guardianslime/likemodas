# likemodas/pages/search_results.py (VERSIÓN FINAL Y CORREGIDA)

import reflex as rx
from ..ui.base import base_page
from ..ui.search_state import SearchState
# --- CAMBIO 1: Importamos el componente correcto ---
from ..ui.components import product_gallery_component

def search_results_page() -> rx.Component:
    """Página que muestra los resultados de la búsqueda."""
    return base_page(
        rx.center(
            rx.vstack(
                rx.heading(f"Resultados para: '{SearchState.search_term}'", size="7"),
                rx.cond(
                    SearchState.search_results,
                    # --- CAMBIO 2: Usamos el componente de galería que ahora espera ProductCardData ---
                    product_gallery_component(posts=SearchState.search_results),
                    
                    # Mensaje si no hay resultados
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
    )