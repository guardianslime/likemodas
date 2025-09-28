# likemodas/ui/components.py (COMPLETO Y CORREGIDO)

import reflex as rx
import math
from likemodas.utils.formatting import format_to_cop
from ..state import AppState, ProductCardData
from reflex.event import EventSpec

def star_rating_display_safe(rating: rx.Var[float], count: rx.Var[int], size: int = 18) -> rx.Component:
    return rx.hstack(
        rx.foreach(
            rx.Var.range(5),
            lambda i: rx.icon(
                "star",
                color=rx.cond(rating > i, "gold", rx.color("gray", 8)),
                style={"fill": rx.cond(rating > i, "gold", "none")},
                size=size,
            )
        ),
        rx.cond(
            count > 0,
            rx.text(f"({count})", size="2", color_scheme="gray", margin_left="0.25em"),
        ),
        align="center",
        spacing="1",
    )

def searchable_select(
    placeholder: str, 
    options: rx.Var[list], 
    on_change_select: EventSpec,
    value_select: rx.Var[str],
    search_value: rx.Var[str],
    on_change_search: EventSpec,
    filter_name: str,
    is_disabled: rx.Var[bool] = False,
) -> rx.Component:
    is_open = AppState.open_filter_name == filter_name
    
    def render_option(option: rx.Var):
        label = rx.cond(isinstance(option, list) | isinstance(option, tuple), option[0], option)
        value = rx.cond(isinstance(option, list) | isinstance(option, tuple), option[1], option)
        return rx.button(
            label,
            on_click=[on_change_select(value), AppState.toggle_filter_dropdown(filter_name)],
            width="100%", variant="soft", color_scheme="gray", justify_content="start"
        )

    return rx.box(
        # --- MODIFICACIÓN CLAVE EN EL BOTÓN ---
        rx.button(
            rx.cond(value_select, value_select, placeholder),
            rx.icon(tag="chevron-down"),
            on_click=AppState.toggle_filter_dropdown(filter_name),
            variant="outline", width="100%", justify_content="space-between",
            color_scheme="gray", size="2", is_disabled=is_disabled,
            # Estilos para permitir que el texto se ajuste
            height="auto",
            white_space="normal",
            text_align="left",
            padding="0.5em 0.75em",
        ),
        # --- FIN DE LA MODIFICACIÓN ---
        rx.cond(
            is_open,
            rx.vstack(
                rx.input(placeholder="Buscar...", value=search_value, on_change=on_change_search),
                rx.scroll_area(
                    rx.vstack(
                        rx.foreach(options, render_option),
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
                        on_click=lambda: remove_handler(prop_name, item),
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


def product_gallery_component(posts: rx.Var[list[ProductCardData]]) -> rx.Component:
    return rx.cond(
        posts,
        rx.flex(
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
                                    style={"position": "absolute", "top": "0.5rem", "left": "0.5rem", "z_index": "1"}
                                ),
                                position="relative", width="260px", height="260px",
                            ),
                            rx.vstack(
                                rx.text(
                                    post.title, 
                                    weight="bold", 
                                    size="6", 
                                    white_space="normal",
                                    text_overflow="initial",
                                    overflow="visible",
                                ),
                                star_rating_display_safe(post.average_rating, post.rating_count, size=24),
                                rx.text(post.price_cop, size="5", weight="medium"),
                                rx.hstack(
                                    rx.badge(
                                        post.shipping_display_text,
                                        color_scheme=rx.cond(post.shipping_cost == 0.0, "green", "gray"),
                                        variant="soft",
                                        size="2",
                                    ),
                                    rx.cond(
                                        post.is_moda_completa_eligible,
                                        rx.tooltip(
                                            rx.badge("Moda Completa", color_scheme="violet", variant="soft", size="2"),
                                            content="Este item cuenta para el envío gratis en compras sobre $200.000"
                                        )
                                    ),
                                    spacing="3",
                                    align="center",
                                ),
                                # --- CORRECCIÓN AQUÍ ---
                                spacing="1", # Cambiado de "1.5" a "1"
                                align_items="start", 
                                width="100%"
                            ),
                            spacing="2", 
                            width="100%",
                            on_click=AppState.open_product_detail_modal(post.id),
                            cursor="pointer",
                        ),
                        rx.spacer(),
                    ),
                    width="290px",
                    height="auto",
                    min_height="450px",
                    bg=rx.color_mode_cond("#f9f9f9", "#111111"),
                    border=rx.color_mode_cond("1px solid #e5e5e5", "1px solid #1a1a1a"),
                    border_radius="8px", box_shadow="md", padding="1em",
                )
            ),
            wrap="wrap", spacing="6", justify="center", width="100%", max_width="1800px",
        )
    )