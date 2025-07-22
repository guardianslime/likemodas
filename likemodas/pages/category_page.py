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
    cat_name: str = ""

    @rx.event
    def load_category_posts(self):
        with rx.session() as session:
            query_filter = [
                BlogPostModel.publish_active == True, 
                BlogPostModel.publish_date < datetime.now()
            ]
            if self.cat_name != "todos":
                try:
                    category_enum = Category(self.cat_name)
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
    return base_page(
        rx.center(
            rx.vstack(
                rx.heading(CategoryPageState.cat_name.to_title(), size="8"),
                rx.cond(
                    CategoryPageState.posts_in_category,
                    product_gallery_component(posts=CategoryPageState.posts_in_category),
                    rx.center(
                        rx.text(f"😔 No hay productos en la categoría '{CategoryPageState.cat_name}'."),
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