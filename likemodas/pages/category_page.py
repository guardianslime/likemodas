# likemodas/pages/category_page.py

import reflex as rx
from ..ui.base import base_page
from ..cart.state import CartState, ProductCardData
from ..ui.components import product_gallery_component
from ..models import BlogPostModel, Category
from sqlmodel import select
from datetime import datetime
import sqlalchemy

class CategoryPageState(CartState):
    """Estado para manejar la página de una categoría específica."""
    
    posts_in_category: list[ProductCardData] = []

    # --- 👇 ESTA ES LA LÍNEA CLAVE Y CORRECTA 👇 ---
    # Una variable simple. Reflex la llenará automáticamente desde la URL.
    category_name: str = ""

    @rx.event
    def load_category_posts(self):
        """Carga los productos que pertenecen a la categoría actual."""
        with rx.session() as session:
            yield super().on_load() 
            
            # Ahora, 'self.category_name' ya tiene el valor correcto de la URL.
            if self.category_name != "todos":
                try:
                    category_enum = Category(self.category_name)
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
    """Página que muestra productos de una categoría específica."""
    return base_page(
        rx.center(
            rx.vstack(
                rx.heading(CategoryPageState.category_name.to_title(), size="8"),
                rx.cond(
                    CategoryPageState.posts_in_category,
                    product_gallery_component(posts=CategoryPageState.posts_in_category),
                    rx.center(
                        rx.text(f"😔 No hay productos en la categoría '{CategoryPageState.category_name}'."),
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