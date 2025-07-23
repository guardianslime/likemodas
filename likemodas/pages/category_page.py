# likemodas/pages/category_page.py

import reflex as rx
from ..ui.base import base_page
from ..ui.components import product_gallery_component
from ..ui.filter_sidebar import filter_sidebar
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
    """Página que muestra productos de una categoría específica."""
    # El encabezado y la galería ahora usan las propiedades del estado base
    gallery_header = rx.hstack(
        filter_sidebar(),
        rx.text("Categorías:", weight="bold", margin_right="1em"),
        rx.button("Ropa", on_click=rx.redirect("/category/ropa"), variant="soft"),
        rx.button("Calzado", on_click=rx.redirect("/category/calzado"), variant="soft"),
        rx.button("Mochilas", on_click=rx.redirect("/category/mochilas"), variant="soft"),
        rx.button("Ver Todo", on_click=rx.redirect("/"), variant="soft"),
        spacing="4", align="center", justify="start", width="100%",
        max_width="1800px", padding_bottom="1em", padding_left="4em"
    )

    return base_page(
        rx.center(
            rx.vstack(
                gallery_header,
                rx.heading(CategoryPageState.category_name.title(), size="8", padding_top="1em"),
                rx.cond(
                    CategoryPageState.filtered_posts,
                    product_gallery_component(posts=CategoryPageState.filtered_posts),
                    rx.center(
                        rx.text(f"😔 No hay productos en la categoría '{CategoryPageState.category_name}'."),
                        min_height="40vh"
                    )
                ),
                spacing="6", width="100%", padding="2em", align="center"
            ),
            width="100%"
        )
    )