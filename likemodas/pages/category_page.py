# likemodas/pages/category_page.py

import reflex as rx
from ..auth.state import SessionState
from ..cart.state import CartState, ProductCardData
from ..ui.components import product_gallery_component, categories_button
from ..models import BlogPostModel, Category
from sqlmodel import select
from datetime import datetime
import sqlalchemy
from ..ui.filter_panel import floating_filter_panel
# --- Nuevas importaciones directas para construir el layout ---
from ..ui.nav import public_navbar
from ..ui.base import fixed_color_mode_button

class CategoryPageState(SessionState):
    # ... tu código de estado existente no cambia ...
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

def category_page() -> rx.Component:
    """
    Página de categoría con un layout manual para forzar la carga de estilos.
    """
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
            rx.heading(CategoryPageState.current_category.title(), size="8"),
            rx.cond(
                CategoryPageState.filtered_posts_in_category,
                product_gallery_component(posts=CategoryPageState.filtered_posts_in_category),
                rx.center(
                    rx.text(f"😔 No hay productos en la categoría '{CategoryPageState.current_category}'."),
                    min_height="40vh"
                )
            ),
            spacing="6", width="100%", padding="2em", align="center"
        ),
        width="100%"
    )

    # --- ESTRUCTURA DE LAYOUT MANUAL ---
    return rx.theme(
        rx.fragment(
            public_navbar(),
            rx.box(
                page_content,
                padding="1em", padding_top="6rem", width="100%", id="my-content-area-el"
            ),
            fixed_color_mode_button(),
        ),
        appearance="dark", has_background=True, panel_background="solid",
        scaling="90%", radius="medium", accent_color="sky"
    )