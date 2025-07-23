# likemodas/pages/search_results.py

import reflex as rx
from ..ui.base import base_page
from ..ui.search_state import SearchState
from ..ui.components import product_gallery_component
# --- 👇 AÑADE LA IMPORTACIÓN DEL SIDEBAR DE FILTROS 👇 ---
from ..ui.filter_sidebar import floating_filter_sidebar

def search_results_page() -> rx.Component:
    """Página que muestra los resultados de la búsqueda, ahora con filtros."""
    return base_page(
        # --- AÑADE EL SIDEBAR DE FILTROS A LA PÁGINA ---
        floating_filter_sidebar(),
        rx.center(
            rx.vstack(
                rx.heading(f"Resultados para: '{SearchState.search_term}'", size="7"),
                rx.cond(
                    SearchState.filtered_posts, # <-- Usa la lista filtrada
                    product_gallery_component(posts=SearchState.filtered_posts),
                    rx.center(
                        rx.text(f"😔 No se encontraron publicaciones con el nombre: '{SearchState.search_term}'"),
                        padding="4em", min_height="40vh"
                    )
                ),
                spacing="6",
                width="100%",
                padding="2em",
                align="center",
                # --- AÑADE LAS PROPIEDADES PARA EL DESPLAZAMIENTO ---
                transition="padding-left 0.3s ease",
                padding_left=rx.cond(
                    SearchState.show_filters, "220px", "0px"
                ),
            ),
            width="100%"
        )
    )