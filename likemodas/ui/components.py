# likemodas/ui/components.py (Versión Corregida y con Diagnóstico)

import reflex as rx
import math

from likemodas.utils.formatting import format_to_cop
from ..state import AppState, ProductCardData
from reflex.event import EventSpec

# La función searchable_select no necesita cambios
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
    is_open = AppState.open_filter_name == filter_name
    return rx.box(
        rx.button(
            rx.cond(value_select, value_select, placeholder),
            rx.icon(tag="chevron-down"),
            on_click=AppState.toggle_filter_dropdown(filter_name),
            variant="outline", width="100%", justify_content="space-between",
            color_scheme="gray", size="2", is_disabled=is_disabled,
        ),
        rx.cond(
            is_open,
            rx.vstack(
                rx.input(placeholder="Buscar...", value=search_value, on_change=on_change_search),
                rx.scroll_area(
                    rx.vstack(
                        rx.foreach(
                            options,
                            lambda option: rx.button(
                                option,
                                on_click=[lambda: on_change_select(option), AppState.toggle_filter_dropdown(filter_name)],
                                width="100%", variant="soft", color_scheme="gray", justify_content="start"
                            )
                        ),
                        spacing="1", width="100%",
                    ),
                    max_height="200px", width="100%", type="auto", scrollbars="vertical",
                ),
                spacing="2", padding="0.75em", bg=rx.color("gray", 3),
                border="1px solid", border_color=rx.color("gray", 7),
                border_radius="md", position="absolute", top="105%",
                width="100%", z_index=10,
            )
        ),
        position="relative", width="100%",
    )


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
    """
    Componente que muestra una galería de productos.
    """
    return rx.flex(
        rx.foreach(
            posts,
            lambda post: rx.box(
                # El vstack principal de la tarjeta ahora tendrá on_click
                rx.vstack(
                    rx.vstack(
                        # Este vstack envuelve la parte superior clickeable que abre el modal
                        rx.box(
                            rx.cond(
                                post.image_urls & (post.image_urls.length() > 0),
                                rx.image(src=rx.get_upload_url(post.image_urls[0]), width="100%", height="260px", object_fit="cover"),
                                rx.box(rx.icon("image_off", size=48), width="100%", height="260px", bg=rx.color("gray", 3), display="flex", align_items="center", justify_content="center")
                            ),
                            width="260px", height="260px"
                        ),
                        rx.vstack(
                            rx.text(post.title, weight="bold", size="6"),
                            _product_card_rating(post),
                            rx.text(post.price_cop, size="6"),
                            spacing="2",
                            align_items="start",
                            width="100%"
                        ),
                        rx.vstack(
                            rx.text(post.title, weight="bold", size="6"),
                            _product_card_rating(post),
                            rx.text(post.price_cop, size="6"),

                            # --- 👇 AÑADE ESTE BLOQUE 👇 ---
                            rx.vstack(
                                rx.cond(
                                    post.shipping_cost == 0.0,
                                    rx.badge("Envío Gratis", color_scheme="green", variant="soft"),
                                    rx.cond(
                                        post.shipping_cost > 0,
                                        rx.text(f"Envío: {format_to_cop(post.shipping_cost)}", size="2"),
                                        rx.text("Envío a convenir", size="2", color_scheme="gray")
                                    )
                                ),
                                rx.cond(
                                    post.seller_free_shipping_threshold > 0,
                                    rx.badge(f"Moda Completa: Envío gratis por {post.seller_free_shipping_threshold}+ items", color_scheme="violet", variant="soft", size="1"),
                                ),
                                spacing="2",
                                align_items="start",
                                margin_top="0.5em",
                                min_height="50px", # Para mantener la alineación de los botones
                            ),
                            # --- FIN DEL BLOQUE ---

                            spacing="2",
                            align_items="start",
                            width="100%"
                        ),
                        spacing="2",
                        width="100%",
                        # Hacemos que esta sección superior sea la que abre el modal
                        on_click=lambda: AppState.open_product_detail_modal(post.id),
                        cursor="pointer",
                    ),

                    rx.spacer(),

                    # --- INICIO DE LA MODIFICACIÓN ---
                    # Añadimos el botón en la parte inferior de la tarjeta
                    rx.button(
                        "Añadir al Carrito",
                        width="100%",
                        # --- INICIO DE LA CORRECCIÓN ---
                        # Reemplaza la lambda por el manejador de eventos de Reflex
                        on_click=[
                            AppState.add_to_cart(post.id),
                            rx.stop_propagation 
                        ],
                    ),
                    # --- FIN DE LA MODIFICACIÓN ---
                ),
                width="290px", 
                height="450px", # La altura se mantiene bien
                bg=rx.color_mode_cond("#f9f9f9", "#111111"),
                border=rx.color_mode_cond("1px solid #e5e5e5", "1px solid #1a1a1a"),
                border_radius="8px", 
                box_shadow="md", 
                padding="1em",
            )
        ),
        wrap="wrap", 
        spacing="6", 
        justify="center", 
        width="100%", 
        max_width="1800px",
    )


def multi_select_component(
    placeholder: str,
    options: rx.Var[list[str]],
    selected_items: rx.Var[list[str]],
    add_handler: rx.event.EventHandler,
    remove_handler: rx.event.EventHandler,
    prop_name: str,
    search_value: rx.Var[str],
    on_change_search: rx.event.EventSpec,
    filter_name: str,
) -> rx.Component:
    """Un componente para seleccionar múltiples opciones con un buscador."""
    return rx.vstack(
        rx.flex(
            rx.foreach(
                selected_items,
                lambda item: rx.badge(
                    item,
                    rx.icon(
                        "x",
                        size=12,
                        cursor="pointer",
                        on_click=remove_handler(prop_name, item),
                        margin_left="0.25em"
                    ),
                    variant="soft", color_scheme="gray", size="2",
                ),
            ),
            wrap="wrap", spacing="2", min_height="36px", padding="0.5em",
            border="1px solid", border_color=rx.color("gray", 7), border_radius="md",
        ),
        searchable_select(
            placeholder=placeholder,
            options=options,
            on_change_select=lambda val: add_handler(prop_name, val),
            value_select="",
            search_value=search_value,
            on_change_search=on_change_search,
            filter_name=filter_name,
        ),
        spacing="2", align_items="stretch", width="100%",
    )