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

    @rx.var
    def category_name(self) -> str:
        """Obtiene el nombre de la categoría desde la URL."""
        return self.router.page.params.get("category_name", "todos")

    @rx.event
    def load_category_posts(self):
        """Carga los productos que pertenecen a la categoría actual."""
        with rx.session() as session:
            # Primero, carga todos los posts como hace el on_load de CartState
            yield super().on_load() 
            
            # Ahora, filtra los posts para esta categoría
            if self.category_name != "todos":
                try:
                    # Valida que la categoría exista
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
                    # Si la categoría no es válida, la lista estará vacía
                    self.posts_in_category = []
            else:
                # Si la categoría es "todos", muestra todos los posts
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