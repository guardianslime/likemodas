# likemodas/ui/components.py

import reflex as rx
import math
from ..state import AppState, ProductCardData
from reflex.event import EventSpec

def searchable_select(
    placeholder: str, 
    options: rx.Var[list[str]], 
    on_change_select: EventSpec,
    value_select: rx.Var[str],
    search_value: rx.Var[str],
    on_change_search: EventSpec,
    filter_name: str,
    is_disabled: rx.Var[bool] = False,
) -> rx.Component:
    # ... (código de searchable_select sin cambios) ...
    pass

def _product_card_rating(post: ProductCardData) -> rx.Component:
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

def product_gallery_component(posts: rx.Var[list[ProductCardData]]) -> rx.Component:
    """Un componente que muestra una galería de productos."""
    return rx.flex(
        rx.foreach(
            posts,
            lambda post: rx.box(
                rx.vstack(
                    rx.vstack(
                        rx.box(
                            rx.cond(
                                post.image_urls & (post.image_urls.length() > 0),
                                rx.image(src=rx.get_upload_url(post.image_urls[0]), width="100%", height="260px", object_fit="cover"),
                                rx.box(rx.icon("image_off", size=48), width="100%", height="260px", bg=rx.color("gray", 3), display="flex", align_items="center", justify_content="center")
                            ),
                            width="260px", height="260px"
                        ),
                        rx.text(post.title, weight="bold", size="6"),
                        rx.text(post.price_cop, size="6"),
                        _product_card_rating(post),
                        spacing="2", align="start",
                        on_click=AppState.open_product_detail_modal(post.id),
                        cursor="pointer",
                        width="100%",
                    ),
                    align="stretch", height="100%"
                ),
                width="290px", height="420px", bg=rx.color_mode_cond("#f9f9f9", "#111111"),
                border=rx.color_mode_cond("1px solid #e5e5e5", "1px solid #1a1a1a"),
                border_radius="8px", box_shadow="md", padding="1em",
            )
        ),
        wrap="wrap", spacing="6", justify="center", width="100%", max_width="1800px",
    )