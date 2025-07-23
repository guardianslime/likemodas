# likemodas/pages/category_page.py

import reflex as rx
from ..ui.base import base_page
from ..ui.components import product_gallery_component
from ..ui.gallery_header import gallery_header
from ..states.gallery_state import ProductGalleryState
from ..models import BlogPostModel, Category
from ..data.schemas import ProductCardData
from sqlmodel import select
from datetime import datetime
import sqlalchemy

class CategoryPageState(ProductGalleryState):
    """
    Estado para la página de categorías, AHORA SIGUIENDO TU PATRÓN.
    """
    
    # NO declaramos 'cat_name' como una variable simple.
    # En su lugar, creamos una propiedad computada para leer el parámetro de la URL.
    @rx.var
    def category_name(self) -> str:
        """Obtiene el nombre de la categoría desde la URL."""
        return self.router.page.params.get("cat_name", "todos")

    @rx.event
    def load_posts(self):
        """Carga los productos de la categoría actual."""
        # Usamos la propiedad computada para obtener el nombre de la categoría.
        category = self.category_name
        
        with rx.session() as session:
            query_filter = [
                BlogPostModel.publish_active == True, 
                BlogPostModel.publish_date < datetime.now()
            ]
            if category != "todos":
                try:
                    category_enum = Category(category)
                    query_filter.append(BlogPostModel.category == category_enum)
                except ValueError:
                    self.all_posts = []
                    return

            statement = (
                select(BlogPostModel)
                .options(sqlalchemy.orm.joinedload(BlogPostModel.comments))
                .where(*query_filter)
                .order_by(BlogPostModel.created_at.desc())
            )
            results = session.exec(statement).unique().all()
            self.all_posts = [
                ProductCardData(
                    id=p.id, title=p.title, price=p.price, images=p.images,
                    average_rating=p.average_rating, rating_count=p.rating_count
                ) for p in results
            ]

def category_page() -> rx.Component:
    """Página de categoría con su propia barra de categorías y filtros."""
    return base_page(
        rx.center(
            rx.vstack(
                gallery_header(),
                rx.heading(CategoryPageState.category_name.title(), size="8", padding_top="1em"),
                rx.cond(
                    CategoryPageState.filtered_posts,
                    product_gallery_component(posts=CategoryPageState.filtered_posts),
                    # ...
                ),
                spacing="6", width="100%", padding="2em", align="center",
                transition="padding-left 0.3s ease",
                padding_left=rx.cond(
                    CategoryPageState.show_filters, "250px", "0px"
                ),
            ),
            width="100%"
        )
    )