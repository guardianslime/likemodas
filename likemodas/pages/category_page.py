# likemodas/pages/category_page.py

import reflex as rx
from ..ui.base import base_page
from ..auth.state import SessionState
from ..cart.state import CartState, ProductCardData
from ..ui.components import product_gallery_component
from ..models import BlogPostModel, Category
from sqlmodel import select
from datetime import datetime
import sqlalchemy

class CategoryPageState(SessionState):
    posts_in_category: list[ProductCardData] = []
    
    # --- CAMBIO 1: Usamos un nombre DIFERENTE para la variable de estado ---
    current_category: str = ""

    @rx.event
    def load_category_posts(self):
        # --- CAMBIO 2: Leemos el parámetro de la URL manualmente ---
        cat_name_from_url = self.router.page.params.get("cat_name", "todos")
        self.current_category = cat_name_from_url

        with rx.session() as session:
            query_filter = [
                BlogPostModel.publish_active == True, 
                BlogPostModel.publish_date < datetime.now()
            ]
            if cat_name_from_url != "todos":
                try:
                    category_enum = Category(cat_name_from_url)
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
                    id=post.id, title=post.title, price=post.price, images=post.images,
                    average_rating=post.average_rating, rating_count=post.rating_count
                ) for post in results
            ]

def category_page() -> rx.Component:
    """Página que muestra productos de una categoría específica."""
    return base_page(
        rx.center(
            rx.vstack(
                # --- CAMBIO 3: Usamos nuestra nueva variable de estado ---
                rx.heading(CategoryPageState.current_category.to_title(), size="8"),
                rx.cond(
                    CategoryPageState.posts_in_category,
                    product_gallery_component(posts=CategoryPageState.posts_in_category),
                    rx.center(
                        rx.text(f"😔 No hay productos en la categoría '{CategoryPageState.current_category}'."),
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