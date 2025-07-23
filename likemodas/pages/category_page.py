# likemodas/pages/category_page.py

import reflex as rx
from ..ui.base import base_page
from ..auth.state import SessionState
from ..cart.state import CartState, ProductCardData
from ..ui.components import product_gallery_component
from ..ui.filter_state import FilterState 
from ..models import BlogPostModel, Category
from sqlmodel import select
from datetime import datetime
import sqlalchemy

class CategoryPageState(SessionState):
    posts_in_category: list[ProductCardData] = []

    # --- 👇 PASO 1: Creamos la propiedad computada, como en tus otros estados 👇 ---
    @rx.var
    def current_category(self) -> str:
        """Obtiene el nombre de la categoría desde la URL, siguiendo el patrón existente."""
        return self.router.page.params.get("cat_name", "todos")

    @rx.event
    def load_category_posts(self):
        # --- 👇 PASO 2: Usamos la propiedad computada para obtener el valor 👇 ---
        category_from_url = self.current_category
        
        with rx.session() as session:
            query_filter = [
                BlogPostModel.publish_active == True, 
                BlogPostModel.publish_date < datetime.now()
            ]
            if category_from_url != "todos":
                try:
                    category_enum = Category(category_from_url)
                    query_filter.append(BlogPostModel.category == category_enum)
                except ValueError:
                    self.posts_in_category = []
                    return

            statement = (
                select(BlogPostModel)
                .options(sqlalchemy.orm.joinedload(BlogPostModel.comments))
                .where(*query_filter)
                .order_by(BlogPostModel.created_at.desc())
            )
            results = session.exec(statement).unique().all()
            self.posts_in_category = [
                ProductCardData(
                    id=p.id, title=p.title, price=p.price, images=p.images,
                    average_rating=p.average_rating, rating_count=p.rating_count
                ) for p in results
            ]
    
    @rx.var
    def filtered_posts_in_category(self) -> list[ProductCardData]:
        """Filtra la lista de posts de la categoría actual."""
        posts_to_filter = self.posts_in_category
        try:
            # Usa self.min_price directamente
            min_p = float(self.min_price) if self.min_price else 0
        except ValueError:
            min_p = 0
        try:
            # Usa self.max_price directamente
            max_p = float(self.max_price) if self.max_price else float('inf')
        except ValueError:
            max_p = float('inf')

        if min_p > 0 or max_p != float('inf'):
            return [p for p in posts_to_filter if (p.price >= min_p and p.price <= max_p)]
        
        return posts_to_filter


def category_page() -> rx.Component:
    return base_page(
        rx.center(
            rx.vstack(
                # --- 👇 PASO 3: La UI usa la propiedad computada con normalidad 👇 ---
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
    )