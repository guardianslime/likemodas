# likemodas/ui/components.py (COMPLETO Y CORREGIDO)

import reflex as rx
import math
from likemodas.utils.formatting import format_to_cop
from ..state import (
    AppState, 
    ProductCardData,
    DEFAULT_LIGHT_BG, DEFAULT_LIGHT_TITLE, DEFAULT_LIGHT_PRICE,
    DEFAULT_DARK_BG, DEFAULT_DARK_TITLE, DEFAULT_DARK_PRICE,
)

from reflex.event import EventSpec

# --- ✨ INICIO: AÑADE ESTE DICCIONARIO DE ESTILO ✨ ---
# Este es el CSS a prueba de fallos para forzar 2 líneas y agregar "..."
TITLE_CLAMP_STYLE = {
    "display": "-webkit-box",
    "-webkit-line-clamp": "2",  # El número de líneas
    "-webkit-box-orient": "vertical",
    "overflow": "hidden",
    "text_overflow": "ellipsis",
}
# --- ✨ FIN ✨ ---

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
        
        # --- 👇 ¡LA CORRECCIÓN ESTÁ AQUÍ! 👇 ---
        return rx.button(
            label,
            on_click=[on_change_select(value), AppState.toggle_filter_dropdown(filter_name)],
            width="100%", 
            variant="soft", 
            color_scheme="gray", 
            justify_content="start",
            type="button",  # <--- Esta línea evita que el botón envíe el formulario.
        )
        # --- 👆 ¡FIN DE LA CORRECCIÓN! 👆 ---

    return rx.box(
        rx.button(
            rx.cond(value_select, value_select, placeholder),
            rx.icon(tag="chevron-down"),
            on_click=AppState.toggle_filter_dropdown(filter_name),
            variant="outline", width="100%", justify_content="space-between",
            color_scheme="gray", size="2", is_disabled=is_disabled,
            height="auto",
            white_space="normal",
            text_align="left",
            padding="0.5em 0.75em",
        ),
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


# --- ✨ 2. REEMPLAZA LA FUNCIÓN product_gallery_component CON ESTA ✨ ---
def product_gallery_component(posts: rx.Var[list[ProductCardData]]) -> rx.Component:
    """
    [VERSIÓN FINAL UNIFICADA]
    Galería de productos que renderiza las tarjetas con el mismo estilo
    visual que la previsualización, aplicando colores y transformaciones de imagen guardadas.
    """
    def _render_single_card(post: ProductCardData) -> rx.Component:
        """Función interna para renderizar una sola tarjeta de producto."""
        
        # 1. Obtiene los estilos de imagen guardados, con valores por defecto
        image_styles = post.image_styles
        zoom = image_styles.get("zoom", 1.0)
        rotation = image_styles.get("rotation", 0)
        offset_x = image_styles.get("offsetX", 0)
        offset_y = image_styles.get("offsetY", 0)
        transform_style = f"scale({zoom}) rotate({rotation}deg) translateX({offset_x}px) translateY({offset_y}px)"

        # 2. Lógica de colores unificada (idéntica a la del state y la previsualización)
        card_bg_color = rx.cond(
            post.use_default_style,
            rx.color_mode_cond(DEFAULT_LIGHT_BG, DEFAULT_DARK_BG),
            rx.cond(
                post.light_card_bg_color & post.dark_card_bg_color,
                rx.color_mode_cond(post.light_card_bg_color, post.dark_card_bg_color),
                post.light_card_bg_color | post.dark_card_bg_color | rx.color_mode_cond(DEFAULT_LIGHT_BG, DEFAULT_DARK_BG)
            )
        )
        title_color = rx.cond(
            post.use_default_style,
            rx.color_mode_cond(DEFAULT_LIGHT_TITLE, DEFAULT_DARK_TITLE),
            rx.cond(
                post.light_title_color & post.dark_title_color,
                rx.color_mode_cond(post.light_title_color, post.dark_title_color),
                post.light_title_color | post.dark_title_color | rx.color_mode_cond(DEFAULT_LIGHT_TITLE, DEFAULT_DARK_TITLE)
            )
        )
        price_color = rx.cond(
            post.use_default_style,
            rx.color_mode_cond(DEFAULT_LIGHT_PRICE, DEFAULT_DARK_PRICE),
            rx.cond(
                post.light_price_color & post.dark_price_color,
                rx.color_mode_cond(post.light_price_color, post.dark_price_color),
                post.light_price_color | post.dark_price_color | rx.color_mode_cond(DEFAULT_LIGHT_PRICE, DEFAULT_DARK_PRICE)
            )
        )

        return rx.box(
            rx.vstack(
                rx.vstack(
                    rx.box(
                        rx.cond(
                            post.main_image_url != "",
                            rx.image(
                                src=rx.get_upload_url(post.main_image_url), 
                                width="100%", height="260px", 
                                object_fit="contain", # Coincide con la previsualización
                                transform=transform_style, # Aplica los estilos guardados
                                transition="transform 0.2s ease-out",
                            ),
                            # Fallback si no hay imagen
                            rx.box(rx.icon("image-off", size=48), width="100%", height="260px", bg=rx.color("gray", 3), display="flex", align_items="center", justify_content="center")
                        ),
                        rx.badge(
                            rx.cond(post.is_imported, "Importado", "Nacional"),
                            color_scheme=rx.cond(post.is_imported, "purple", "cyan"),
                            variant="solid",
                            style={"position": "absolute", "top": "0.5rem", "left": "0.5rem", "z_index": "1"}
                        ),
                        position="relative",
                        width="100%", height="260px",
                        overflow="hidden",
                        bg=rx.color_mode_cond("white", rx.color("gray", 3)),
                    ),
                    rx.vstack(
                        # --- ✨ INICIO DE LA CORRECCIÓN ✨ ---
                        rx.text(
                            post.title, 
                            weight="bold", 
                            size="6", 
                            width="100%", 
                            color=title_color,
                            style=TITLE_CLAMP_STYLE  # <--- REEMPLAZA no_of_lines CON ESTO
                        ),
                        star_rating_display_safe(post.average_rating, post.rating_count, size=24),
                        rx.text(post.price_cop, size="5", weight="medium", color=price_color),
                        rx.spacer(),
                        rx.vstack(
                            rx.hstack(
                                rx.badge(post.shipping_display_text, color_scheme="gray", variant="soft", size="2"),
                                rx.cond(
                                    post.is_moda_completa_eligible,
                                    rx.tooltip(rx.badge("Moda Completa", color_scheme="violet", variant="soft", size="2"), content=post.moda_completa_tooltip_text),
                                ),
                                spacing="3", align="center",
                            ),
                            rx.cond(
                                post.combines_shipping,
                                rx.tooltip(rx.badge("Envío Combinado", color_scheme="teal", variant="soft", size="2"), content=post.envio_combinado_tooltip_text),
                            ),
                            spacing="1", align_items="start", width="100%",
                        ),
                        spacing="2", align_items="start", width="100%", padding="1em", flex_grow="1",
                    ),
                    spacing="0", align_items="stretch", width="100%",
                ),
                # El on_click abre el modal de detalle del producto
                on_click=AppState.open_product_detail_modal(post.id),
                cursor="pointer",
                height="100%"
            ),
            width="290px", 
            height="480px", # Altura fija para consistencia
            bg=card_bg_color,
            border=rx.color_mode_cond("1px solid #e5e5e5", "1px solid #1a1a1a"),
            border_radius="8px", 
            box_shadow="md",
            overflow="hidden"
        )

    return rx.cond(
        posts,
        rx.flex(
            rx.foreach(posts, _render_single_card),
            wrap="wrap", spacing="6", justify="center", width="100%", max_width="1800px",
        )
    )