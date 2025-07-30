# likemodas/pages/category_page.py

import reflex as rx
from..ui.base import base_page
from..auth.state import SessionState
from..cart.state import CartState
from..ui.components import product_gallery_component
from..ui.filter_panel import floating_filter_panel
from..ui.skeletons import skeleton_product_gallery

def category_page() -> rx.Component:
    """Página de categoría que muestra productos filtrados, con esqueleto de carga."""
    
    gallery_content = product_gallery_component(posts=CartState.filtered_posts)
    
    no_products_message = rx.center(
        rx.text(f"😔 No hay productos en la categoría '{CartState.current_category}' que coincidan con los filtros."),
        min_height="40vh"
    )

    page_content = rx.center(
        rx.vstack(
            rx.cond(
                SessionState.is_hydrated,
                rx.cond(
                    ~SessionState.is_admin,
                    floating_filter_panel()
                )
            ),
            rx.heading(CartState.current_category.title(), size="8", margin_bottom="1em"),
            
            # --- LÓGICA DE RENDERIZADO CONDICIONAL ---
            rx.cond(
                CartState.is_loading,
                # Muestra el esqueleto de la galería mientras se cargan los datos
                skeleton_product_gallery(count=12), 
                # Una vez cargado, decide si mostrar la galería o un mensaje de "no encontrado"
                rx.cond(
                    CartState.filtered_posts,
                    gallery_content,
                    no_products_message
                )
            ),
            spacing="6", 
            width="100%", 
            padding="2em", 
            align="center"
        ),
        width="100%"
    )
    
    return base_page(
        rx.cond(
            CartState.is_loading,
            skeleton_product_gallery(count=12), # Show Skeleton
            rx.cond(
                CartState.filtered_posts,
                product_gallery_component(posts=CartState.filtered_posts), # Show Gallery
                no_products_message # Show No Products Message
            )
        )
    )