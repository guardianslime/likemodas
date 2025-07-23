# likemodas/pages/category_page.py

import reflex as rx
from ..ui.base import base_page
from ..auth.state import SessionState
from ..cart.state import CartState, ProductCardData
from ..ui.components import product_gallery_component
from ..ui.filter_sidebar import filter_sidebar # <-- Importa el nuevo sidebar
from ..models import BlogPostModel, Category
from sqlmodel import select
from datetime import datetime
import sqlalchemy

class CategoryPageState(SessionState):
    cat_name: str = ""

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
            self.all_posts = [
                ProductCardData(
                    id=post.id, title=post.title, price=post.price, images=post.images,
                    average_rating=post.average_rating, rating_count=post.rating_count
                ) for post in results
            ]

def category_page() -> rx.Component:
    """Página de categoría con su propia barra de categorías y filtros."""
    return base_page(
        rx.center(
            rx.vstack(
                # --- AÑADIMOS EL MISMO ENCABEZADO QUE EN LA PÁGINA PRINCIPAL ---
                rx.hstack(
                    filter_sidebar(),
                    rx.text("Categorías:", weight="bold", margin_right="1em"),
                    rx.button("Ropa", on_click=rx.redirect("/category/ropa"), variant="soft"),
                    rx.button("Calzado", on_click=rx.redirect("/category/calzado"), variant="soft"),
                    rx.button("Mochilas", on_click=rx.redirect("/category/mochilas"), variant="soft"),
                    rx.button("Ver Todo", on_click=rx.redirect("/"), variant="soft"),
                    spacing="4", align="center", justify="start", width="100%",
                    max_width="1800px", padding_bottom="1em", padding_left="4em"
                ),
                rx.heading(CategoryPageState.current_category.title(), size="8", padding_top="1em"),
                # --- CAMBIO: Muestra los productos filtrados ---
                rx.cond(
                    CategoryPageState.filtered_posts,
                    product_gallery_component(posts=CategoryPageState.filtered_posts),
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