# likemodas/blog/page.py (VERSIÓN REFACTORIZADA)

import reflex as rx
from ..ui.base import base_page 
from ..cart.state import CartState 
from ..navigation import routes
import math
from ..models import BlogPostModel
# --- 👇 CAMBIO 1: Importa los dos componentes ---
from ..ui.components import product_gallery_component, categories_button
from ..ui.filter_panel import floating_filter_panel
# --- 👇 CAMBIO 2: Importa SessionState para la condición del admin ---
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

# --- ✨ NUEVO COMPONENTE REUTILIZABLE --- ✨
def product_gallery_component(posts: rx.Var[list[BlogPostModel]]) -> rx.Component:
    """Un componente que muestra una galería de productos."""
    return rx.flex(
        rx.foreach(
            posts,
            lambda post: rx.box(
                rx.vstack(
                    rx.link(
                        rx.vstack(
                            rx.box(
                                rx.cond(
                                    post.images & (post.images.length() > 0),
                                    rx.image(
                                        src=rx.get_upload_url(post.images[0]),
                                        width="100%", height="100%", object_fit="cover", border_radius="md",
                                    ),
                                    rx.box(
                                        "Sin imagen", width="100%", height="100%", bg="#eee",
                                        align="center", justify="center", display="flex", border_radius="md"
                                    )
                                ),
                                position="relative", width="260px", height="260px"
                            ),
                            rx.text(post.title, weight="bold", size="6", color=rx.color_mode_cond("black", "white")),
                            rx.text(rx.cond(post.price, "$" + post.price.to(str), "$0.00"), color=rx.color_mode_cond("black", "white"), size="6"),
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

# --- ✨ PÁGINA SIMPLIFICADA USANDO EL NUEVO COMPONENTE --- ✨
def blog_public_page():
    """Página pública que ahora es la principal y muestra la galería."""
    return rx.fragment(
        rx.cond(
            SessionState.is_hydrated,
            rx.cond(
                ~SessionState.is_admin,
                floating_filter_panel()
            )
        ),
        base_page(
            rx.center(
                rx.vstack(
                    # --- 👇 CORRECCIÓN: Se elimina el hstack duplicado y se deja solo el componente ---
                    categories_button(),
                    
                    product_gallery_component(posts=CartState.filtered_posts),
                    spacing="6", 
                    width="100%", 
                    padding="2em", 
                    align="center"
                ),
                width="100%"
            )
        )
    )