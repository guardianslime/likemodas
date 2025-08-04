# likemodas/blog/page.py (VERSIÓN REFACTORIZADA)

import reflex as rx
from ..cart.state import CartState 
from ..navigation import routes
import math
from ..models import BlogPostModel
from ..ui.components import product_gallery_component, categories_button
from ..ui.filter_panel import floating_filter_panel
from ..auth.state import SessionState



def _product_card_rating(post: BlogPostModel) -> rx.Component:
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
        rx.box(height="21px")
    )



# --- ✨ PÁGINA SIMPLIFICADA USANDO EL NUEVO COMPONENTE --- ✨
def blog_public_page_content():
    """Página pública que ahora es la principal y muestra la galería."""
    return rx.center(
        rx.vstack(
            rx.cond(
                SessionState.is_hydrated,
                rx.cond(
                    ~SessionState.is_admin,
                    floating_filter_panel()
                )
            ),
            product_gallery_component(posts=CartState.filtered_posts),
            spacing="6", 
            width="100%", 
            padding="2em", 
            align="center"
        ),
        width="100%"
    )