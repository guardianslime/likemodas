# likemodas/ui/components.py (CORREGIDO Y REFORZADO)

import reflex as rx
import math
from likemodas.utils.formatting import format_to_cop
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
    return rx.cond(
        post.rating_count > 0,
        rx.hstack(
            rx.foreach(post.full_stars, lambda _: rx.icon("star", color="gold", size=18)),
            rx.cond(post.has_half_star, rx.icon("star_half", color="gold", size=18)),
            rx.foreach(post.empty_stars, lambda _: rx.icon("star", color=rx.color("gray", 8), size=18)),
            rx.text(f"({post.rating_count})", size="2", color_scheme="gray", margin_left="0.25em"),
            align="center", spacing="1",
        ),
        rx.box(height="21px")
    )

def product_gallery_component(posts: rx.Var[list[ProductCardData]]) -> rx.Component:
    return rx.flex(
        rx.foreach(
            posts,
            lambda post: rx.box(
                rx.vstack(
                    rx.vstack(
                        rx.box(
                            rx.cond(
                                post.variants & (post.variants.length() > 0),
                                rx.image(src=rx.get_upload_url(post.variants[0].get("image_url", "")), width="100%", height="260px", object_fit="cover"),
                                rx.box(rx.icon("image_off", size=48), width="100%", height="260px", bg=rx.color("gray", 3), display="flex", align_items="center", justify_content="center")
                            ),
                            rx.badge(
                                rx.cond(post.is_imported, "Importado", "Nacional"),
                                color_scheme=rx.cond(post.is_imported, "purple", "cyan"),
                                variant="solid",
                                style={
                                    "position": "absolute",
                                    "top": "0.5rem",
                                    "left": "0.5rem",
                                    "z_index": "1",
                                }
                            ),
                            position="relative",
                            width="260px",
                            height="260px",
                        ),
                        rx.vstack(
                            rx.text(post.title, weight="bold", size="6", no_of_lines=1),
                            _product_card_rating(post),
                            rx.text(post.price_cop, size="5", weight="medium"),
                            rx.badge(
                                post.shipping_display_text,
                                color_scheme=rx.cond(post.shipping_cost == 0.0, "green", "gray"),
                                variant="soft",
                                margin_top="0.5em",
                            ),
                            rx.cond(
                                post.is_moda_completa_eligible,
                                rx.tooltip(
                                    rx.badge("Moda Completa", color_scheme="violet", variant="soft", size="1"),
                                    content="Este item cuenta para el envío gratis en compras sobre $200.000"
                                )
                            ),
                            spacing="2",
                            align_items="start",
                            width="100%"
                        ),
                        spacing="2",
                        width="100%",
                        on_click=lambda: AppState.open_product_detail_modal(post.id),
                        cursor="pointer",
                    ),
                    rx.spacer(),
                    rx.button(
                        "Añadir al Carrito",
                        width="100%",
                        on_click=[
                            AppState.add_to_cart(post.id),
                            rx.stop_propagation
                        ],
                    ),
                ),
                width="290px",
                height="520px",
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

# --- INICIO DEL COMPONENTE CORREGIDO ---
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
    """Un componente para seleccionar múltiples opciones con un buscador (VERSIÓN CORREGIDA)."""
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
                        # Se restaura la forma explícita de llamar al manejador
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
            # Se restaura la forma explícita de llamar al manejador
            on_change_select=lambda val: add_handler(prop_name, val),
            value_select="",
            search_value=search_value,
            on_change_search=on_change_search,
            filter_name=filter_name,
        ),
        spacing="2", align_items="stretch", width="100%",
    )
# --- FIN DEL COMPONENTE CORREGIDO ---