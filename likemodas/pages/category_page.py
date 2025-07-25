import reflex as rx
from ..ui.base import base_page
from ..auth.state import SessionState
from ..cart.state import CartState, ProductCardData
# --- 👇 CAMBIO 1: Importa los dos componentes ---
from ..ui.components import product_gallery_component, categories_button
from ..models import BlogPostModel, Category
from sqlmodel import select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql.expression import cast
from sqlalchemy import String, cast
from datetime import datetime
import sqlalchemy
from ..ui.filter_panel import floating_filter_panel

    

# --- ✨ CÓDIGO CORREGIDO PARA LA PÁGINA DE CATEGORÍA --- ✨
def category_page() -> rx.Component:
    page_content = rx.center(
        rx.vstack(
            rx.cond(
                SessionState.is_hydrated,
                rx.cond(
                    ~SessionState.is_admin,
                    rx.fragment(
                        floating_filter_panel(),
                        categories_button()
                    )
                )
            ),
            # --- ✨ Usa la variable de estado central 'current_category' ---
            rx.heading(CartState.current_category.title(), size="8"),
            rx.cond(
                # --- ✨ Usa la propiedad de filtrado unificada ---
                CartState.filtered_posts,
                product_gallery_component(posts=CartState.filtered_posts),
                rx.center(
                    rx.text(f"😔 No hay productos en la categoría '{CartState.current_category}'."),
                    min_height="40vh"
                )
            ),
            spacing="6", width="100%", padding="2em", align="center"
        ),
        width="100%"
    )
    
    return base_page(page_content)