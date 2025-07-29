import reflex as rx
import math
from ..navigation import routes
from ..cart.state import CartState, ProductCardData
from reflex.event import EventSpec
from ..auth.state import SessionState

def searchable_select(
    placeholder: str, 
    options: rx.Var[list[str]], 
    on_change_select: EventSpec,
    value_select: rx.Var[str],
    search_value: rx.Var[str],
    on_change_search: EventSpec,
    filter_name: str,
    is_disabled: rx.Var[bool] = False, # <-- ✨ LÍNEA AÑADIDA
) -> rx.Component:
    """
    Un componente de selección personalizado con opción de búsqueda y deshabilitado.
    """
    is_open = SessionState.open_filter_name == filter_name

    return rx.box(
        rx.button(
            rx.cond(value_select, value_select, placeholder),
            rx.icon(tag="chevron-down"),
            on_click=SessionState.toggle_filter_dropdown(filter_name),
            variant="outline",
            width="100%",
            justify_content="space-between",
            color_scheme="gray",
            size="2",
            is_disabled=is_disabled, # <-- ✨ LÍNEA AÑADIDA
        ),
        rx.cond(
            is_open,
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
                            lambda option: rx.button(
                                option,
                                on_click=[
                                    lambda: on_change_select(option),
                                    SessionState.toggle_filter_dropdown(filter_name)
                                ],
                                width="100%",
                                variant="soft", 
                                color_scheme="gray",
                                justify_content="start"
                            )
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    max_height="200px",
                    width="100%",
                    type="auto",
                    scrollbars="vertical",
                ),
                spacing="2",
                padding="0.75em",
                bg=rx.color("gray", 3),
                border="1px solid",
                border_color=rx.color("gray", 7),
                border_radius="md",
                position="absolute",
                top="105%",
                width="100%",
                z_index=10,
            )
        ),
        position="relative",
        width="100%",
    )

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
    """Un componente para mostrar la calificación global en las tarjetas de producto."""
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
            rx.text(f"{post.average_rating:.1f}", size="2", weight="bold"), # Puntuación
            rx.text(f"({post.rating_count})", size="2", color_scheme="gray"), # Cantidad
            align="center", spacing="1",
        ),
        rx.box(height="21px")
    )

def product_gallery_component(posts: rx.Var[list[ProductCardData]]) -> rx.Component:
    """Un componente reutilizable que muestra una galería de productos."""
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
                            rx.text(post.price_cop, color=rx.color_mode_cond("black", "white"), size="6"), # ✅ CAMBIO AQUÍ
                            _product_card_rating(post), # Usamos la función mejorada
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