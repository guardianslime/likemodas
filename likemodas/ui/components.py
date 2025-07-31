import reflex as rx
import math
from ..navigation import routes
from ..cart.state import CartState, ProductCardData
from.skeletons import skeleton_product_gallery
from reflex.event import EventSpec
from ..auth.state import SessionState
from ..models.product_data import ProductCardData
from sqlalchemy.orm import joinedload
from typing import List
from sqlmodel import select
from datetime import datetime


class SearchState(rx.State):
    """El único y definitivo estado para la búsqueda."""
    search_term: str = ""
    search_results: List[ProductCardData] = []
    search_performed: bool = False

    @rx.event
    def perform_search(self):
        """Ejecuta la búsqueda, transforma los datos y redirige."""
        from ..models import BlogPostModel

        term = self.search_term.strip()
        if not term:
            return

        with rx.session() as session:
            statement = (
                select(BlogPostModel)
                .options(joinedload(BlogPostModel.comments))
                .where(
                    BlogPostModel.publish_active == True,
                    BlogPostModel.publish_date < datetime.now(),
                    BlogPostModel.title.ilike(f"%{term}%")
                )
                .order_by(BlogPostModel.created_at.desc())
            )
            results = session.exec(statement).unique().all()
            self.search_results = [
                ProductCardData(
                    id=post.id,
                    title=post.title,
                    price=post.price,
                    image_urls=post.image_urls,
                    average_rating=post.average_rating,
                    rating_count=post.rating_count
                )
                for post in results
            ]

        self.search_performed = True 
        return rx.redirect("/search-results")
    
# ... (El resto del archivo 'components.py' no necesita cambios) ...

def categories_button() -> rx.Component:
    """Un componente reutilizable para el botón desplegable de categorías."""
    return rx.hstack(
        rx.popover.root(
            rx.popover.trigger(
                rx.button(
                    "Categorías", 
                    variant="outline",
                    size="3",
                    color=rx.color_mode_cond("black", "white"),
                    border_radius="full",
                    style={"border_color": rx.color_mode_cond("black", "white")},
                )
            ),
            rx.popover.content(
                rx.hstack(
                    rx.button("Ropa", on_click=rx.redirect("/category/ropa"), variant="soft"),
                    rx.button("Calzado", on_click=rx.redirect("/category/calzado"), variant="soft"),
                    rx.button("Mochilas", on_click=rx.redirect("/category/mochilas"), variant="soft"),
                    rx.button("Ver Todo", on_click=rx.redirect("/"), variant="soft"),
                    spacing="3",
                ),
                padding="0.5em",
                side="right",
                align="center",
            ),
        ),
        justify="start",
        width="100%",
        max_width="1800px",
        padding_bottom="1em"
    )

def _product_card_rating(post: ProductCardData) -> rx.Component:
    """Muestra la calificación con estrellas para una tarjeta de producto."""
    average_rating = post.average_rating
    rating_count = post.rating_count
    
    full_stars = rx.Var.range(math.floor(average_rating))
    has_half_star = (average_rating - math.floor(average_rating)) >= 0.5
    empty_stars = rx.Var.range(5 - math.ceil(average_rating))

    return rx.cond(
        rating_count > 0,
        rx.hstack(
            rx.foreach(full_stars, lambda _: rx.icon("star", color="gold", size=18)),
            rx.cond(has_half_star, rx.icon("star_half", color="gold", size=18), rx.fragment()),
            rx.foreach(empty_stars, lambda _: rx.icon("star", color=rx.color("gray", 8), size=18)),
            rx.text(f"({rating_count})", size="2", color_scheme="gray", margin_left="0.25em"),
            align="center", spacing="1",
        ),
        # Si no hay calificaciones, deja un espacio vacío para mantener el diseño alineado
        rx.box(height="21px")
    )

def product_gallery_component(posts: rx.Var[list[ProductCardData]]) -> rx.Component:
    """Un componente que muestra una galería de productos."""
    return rx.flex(
        rx.foreach(
            posts,
            lambda post: rx.box(
                rx.vstack(
                    rx.link(
                        rx.vstack(
                            rx.box(
                                # --- ✅ SOLUCIÓN AL ERROR DE IMAGEN ---
                                # Se añade `rx.cond` para verificar si la lista `image_urls`
                                # no está vacía ANTES de intentar acceder a `image_urls[0]`.
                                # Si está vacía, muestra un placeholder.
                                rx.cond(
                                    post.image_urls & (post.image_urls.length() > 0),
                                    rx.image(
                                        src=rx.get_upload_url(post.image_urls[0]),
                                        width="100%", height="100%", object_fit="cover",
                                    ),
                                    rx.box(
                                        rx.vstack(
                                            rx.icon("image_off", size=48, color=rx.color("gray", 8)),
                                            rx.text("Sin imagen", size="2", color=rx.color("gray", 8)),
                                            align="center",
                                            justify="center",
                                        ),
                                        width="100%", height="100%", bg=rx.color("gray", 3),
                                        display="flex", border_radius="md"
                                    )
                                ),
                                position="relative", width="260px", height="260px"
                            ),
                            rx.text(post.title, weight="bold", size="6", color=rx.color_mode_cond("black", "white")),
                            rx.text(post.price_formatted, color=rx.color_mode_cond("black", "white"), size="6"),
                            _product_card_rating(post),
                            spacing="2", align="start"
                        ),
                        href=f"{routes.BLOG_PUBLIC_DETAIL_ROUTE}/{post.id}"
                    ),
                    rx.spacer(),
                    rx.button(
                        "Añadir al Carrito",
                        on_click=lambda: CartState.add_to_cart(post.id),
                        width="100%",
                    ),
                    align="center", spacing="2", height="100%"
                ),
                width="290px", 
                height="450px",
                bg=rx.color_mode_cond("#f9f9f9", "#111111"),
                border=rx.color_mode_cond("1px solid #e5e5e5", "1px solid #1a1a1a"),
                border_radius="8px",
                box_shadow="md",
                padding="1em",
            )
        ),
        wrap="wrap", spacing="6", justify="center", width="100%", max_width="1800px",
    )
