# -----------------------------------------------------------------------------
# likemodas/ui/components.py (NUEVO ARCHIVO Y CORRECCIONES)
# -----------------------------------------------------------------------------
import reflex as rx
import math
from typing import List
from reflex.event import EventSpec
from ..navigation import routes
from ..cart.state import CartState, ProductCardData

# ✅ SOLUCIÓN: Se define el componente que faltaba.
def searchable_select(
    placeholder: str,
    options: rx.Var[List[str]],
    on_change_select: rx.EventChain,
    value_select: rx.Var[str],
    search_value: rx.Var[str],
    on_change_search: rx.EventChain,
    filter_name: str,
    is_disabled: rx.Var[bool] = False,
) -> rx.Component:
    """Un componente de selección con búsqueda integrada dentro de un popover."""
    return rx.popover.root(
        rx.popover.trigger(
            rx.button(
                rx.hstack(
                    rx.text(rx.cond(value_select, value_select, placeholder), color_scheme="gray", width="100%", text_align="left"),
                    rx.icon("chevron-down"),
                    justify="between",
                    width="100%",
                ),
                variant="outline",
                width="100%",
                is_disabled=is_disabled,
            )
        ),
        rx.popover.content(
            rx.vstack(
                rx.input(
                    placeholder="Buscar...",
                    value=search_value,
                    on_change=on_change_search,
                ),
                rx.scroll_area(
                    rx.vstack(
                        rx.foreach(
                            options,
                            lambda option: rx.popover.close(
                                rx.button(
                                    option,
                                    on_click=lambda: on_change_select(option),
                                    width="100%",
                                    variant="ghost",
                                    justify_content="start",
                                )
                            ),
                        ),
                        width="100%",
                    ),
                    max_height="200px",
                    width="100%",
                ),
                spacing="2",
                width="100%",
            ),
            style={"width": "var(--trigger-width)"},
        ),
    )

# Componentes movidos aquí para una mejor estructura
def categories_button() -> rx.Component:
    """Botón desplegable de categorías."""
    return rx.hstack(
        rx.popover.root(
            rx.popover.trigger(
                rx.button(
                    "Categorías", variant="outline", size="3",
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
                padding="0.5em", side="right", align="center",
            ),
        ),
        justify="start", width="100%", max_width="1800px", padding_bottom="1em"
    )

def _product_card_rating(post: ProductCardData) -> rx.Component:
    """Muestra la calificación con estrellas para una tarjeta de producto."""
    average_rating, rating_count = post.average_rating, post.rating_count
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
    """Componente que muestra una galería de productos."""
    return rx.flex(
        rx.foreach(
            posts,
            lambda post: rx.box(
                rx.vstack(
                    rx.link(
                        rx.vstack(
                            rx.box(
                                rx.cond(
                                    post.image_urls & (post.image_urls.length() > 0),
                                    rx.image(src=rx.get_upload_url(post.image_urls[0]), width="100%", height="100%", object_fit="cover"),
                                    rx.box(
                                        rx.vstack(
                                            rx.icon("image_off", size=48, color=rx.color("gray", 8)),
                                            rx.text("Sin imagen", size="2", color=rx.color("gray", 8)),
                                            align="center", justify="center",
                                        ),
                                        width="100%", height="100%", bg=rx.color("gray", 3), display="flex", border_radius="md"
                                    )
                                ),
                                position="relative", width="260px", height="260px"
                            ),
                            rx.text(post.title, weight="bold", size="6", color=rx.color_mode_cond("black", "white")),
                            rx.text(post.price_cop, color=rx.color_mode_cond("black", "white"), size="6"),
                            _product_card_rating(post),
                            spacing="2", align="start"
                        ),
                        href=f"{routes.BLOG_PUBLIC_DETAIL_ROUTE}/{post.id}"
                    ),
                    rx.spacer(),
                    rx.button("Añadir al Carrito", on_click=lambda: CartState.add_to_cart(post.id), width="100%"),
                    align="center", spacing="2", height="100%"
                ),
                width="290px", height="450px",
                bg=rx.color_mode_cond("#f9f9f9", "#111111"),
                border=rx.color_mode_cond("1px solid #e5e5e5", "1px solid #1a1a1a"),
                border_radius="8px", box_shadow="md", padding="1em",
            )
        ),
        wrap="wrap", spacing="6", justify="center", width="100%", max_width="1800px",
    )