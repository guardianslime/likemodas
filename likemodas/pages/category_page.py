# likemodas/pages/category_page.py

import reflex as rx
from ..ui.base import base_page
from ..auth.state import SessionState
from ..cart.state import CartState, ProductCardData
from ..ui.components import product_gallery_component, categories_button
from ..models import BlogPostModel, Category
from sqlmodel import select
from datetime import datetime
import sqlalchemy
from ..ui.filter_panel import floating_filter_panel

# La clase de estado no cambia
class CategoryPageState(SessionState):
    posts_in_category: list[ProductCardData] = []
    
    @rx.var
    def current_category(self) -> str:
        return self.router.page.params.get("cat_name", "todos")

    @rx.event
    def load_category_posts(self):
        # ... tu evento on_load no cambia ...
        pass
    
    @rx.var
    def filtered_posts_in_category(self) -> list[ProductCardData]:
        # ... tu var computada no cambia ...
        return []

# --- VERSIÓN MÍNIMA PARA DEPURACIÓN ---
def category_page() -> rx.Component:
    """Este componente ahora SOLO devuelve el contenido de la página de categoría."""
    return rx.center(
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
            rx.heading(CategoryPageState.current_category.title(), size="8"),
            
            # --- GALERÍA TEMPORALMENTE DESACTIVADA ---
            # rx.cond(
            #     CategoryPageState.filtered_posts_in_category,
            #     product_gallery_component(posts=CategoryPageState.filtered_posts_in_category),
            #     rx.center(
            #         rx.text(f"😔 No hay productos en la categoría '{CategoryPageState.current_category}'."),
            #         min_height="40vh"
            #     )
            # ),
            
            spacing="6", width="100%", padding="2em", align="center"
        ),
        width="100%"
    )
    
    return base_page(page_content)