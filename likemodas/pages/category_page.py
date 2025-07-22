# likemodas/pages/category_page.py

import reflex as rx
from ..ui.base import base_page
from ..cart.state import CartState, ProductCardData
from ..ui.components import product_gallery_component
from ..models import BlogPostModel, Category
from sqlmodel import select
from datetime import datetime
import sqlalchemy
from ..auth.state import SessionState

class CategoryPageState(SessionState):
    """Estado para manejar la página de una categoría específica."""
    # --- 👇 CAMBIO 1: Renombramos la variable 👇 ---

    cat_name: str = ""

    @rx.event
    def load_category_posts(self):
        """Carga los productos que pertenecen a la categoría actual."""
        with rx.session() as session:
            
            # --- 👇 CAMBIO 2: Usamos el nuevo nombre de la variable 👇 ---
            if self.cat_name != "todos":
                try:
                    category_enum = Category(self.cat_name)
                    statement = (
                        select(BlogPostModel)
                        .options(sqlalchemy.orm.joinedload(BlogPostModel.comments))
                        .where(
                            BlogPostModel.publish_active == True, 
                            BlogPostModel.publish_date < datetime.now(),
                            BlogPostModel.category == category_enum
                        )
                        .order_by(BlogPostModel.created_at.desc())
                    )
                    results = session.exec(statement).unique().all()
                    self.posts_in_category = [
                        ProductCardData(
                            id=post.id, title=post.title, price=post.price, images=post.images,
                            average_rating=post.average_rating, rating_count=post.rating_count
                        ) for post in results
                    ]
                except ValueError:
                    self.posts_in_category = []
            else:
                self.posts_in_category = self.posts

    def category_page() -> rx.Component:
        """Página simplificada para depuración."""
        return base_page(
            rx.center(
                rx.heading(f"Categoría: {CategoryPageState.cat_name}"),
                min_height="85vh"
            )
        )
        