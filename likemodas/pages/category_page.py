# likemodas/pages/category_page.py (CORREGIDO)

import reflex as rx
from ..state import AppState
from ..ui.components import product_gallery_component
from ..ui.filter_panel import floating_filter_panel
from ..ui.skeletons import skeleton_product_gallery

def category_content() -> rx.Component:
    """Página de categoría que muestra productos filtrados, usando AppState."""
    # Asegúrate de tener una propiedad `filtered_posts` en tu AppState
    # que filtre la lista `posts` según los filtros activos.
    gallery_content = product_gallery_component(posts=AppState.filtered_posts) 
    
    no_products_message = rx.center(
        rx.text(f"😔 No hay productos en la categoría '{AppState.current_category}' que coincidan con los filtros."),
        min_height="40vh"
    )
    
    page_content = rx.vstack(
        rx.cond(
            AppState.is_hydrated,
            rx.cond(~AppState.is_admin, floating_filter_panel())
        ),
        rx.heading(AppState.current_category.title(), size="8", margin_bottom="1em"),
        rx.cond(
            AppState.is_loading,
            skeleton_product_gallery(count=12),
            rx.cond(AppState.filtered_posts, gallery_content, no_products_message)
        ),
        spacing="6", 
        width="100%", 
        padding="2em", 
        align="center"
    )
    return rx.box(page_content, width="100%")
