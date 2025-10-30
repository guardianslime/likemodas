# En: likemodas/ui/components.py (COMPLETO Y CORREGIDO)

import reflex as rx
import math
from likemodas.utils.formatting import format_to_cop

from ..state import (
    AppState,
    ProductCardData,
    DEFAULT_LIGHT_BG, DEFAULT_LIGHT_TITLE, DEFAULT_LIGHT_PRICE,
    DEFAULT_DARK_BG, DEFAULT_DARK_TITLE, DEFAULT_DARK_PRICE,
    # --- ✨ AÑADIR ESTAS DOS ✨ ---
    DEFAULT_LIGHT_IMAGE_BG, DEFAULT_DARK_IMAGE_BG
    # --- FIN ✨ ---
)

from reflex.event import EventSpec

# --- ESTILO PARA EL TÍTULO (SIN CAMBIOS) ---
TITLE_CLAMP_STYLE = {
    "display": "-webkit-box",
    "-webkit-line-clamp": "2",
    "-webkit-box-orient": "vertical",
    "overflow": "hidden",
    "text_overflow": "ellipsis",
}

# --- star_rating_display_safe (SIN CAMBIOS) ---
def star_rating_display_safe(rating: rx.Var[float], count: rx.Var[int], size: int = 18) -> rx.Component:
    """Muestra estrellas de calificación de forma segura."""
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

# --- searchable_select (SIN CAMBIOS) ---
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
            width="100%", variant="soft", color_scheme="gray",
            justify_content="start", type="button",
        )

    return rx.box(
        rx.button(
            rx.cond(value_select, value_select, placeholder),
            rx.icon(tag="chevron-down"),
            on_click=AppState.toggle_filter_dropdown(filter_name),
            variant="outline", width="100%", justify_content="space-between",
            color_scheme="gray", size="2", is_disabled=is_disabled,
            height="auto", white_space="normal", text_align="left",
            padding="0.5em 0.75em", type="button",
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

# --- multi_select_component (SIN CAMBIOS) ---
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
                        "x", size=12, cursor="pointer",
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


# --- FUNCIÓN product_gallery_component (CON LA LÓGICA DE APARIENCIA CORREGIDA) ---

def product_gallery_component(posts: rx.Var[list[ProductCardData]]) -> rx.Component:
    """
    [VERSIÓN FINAL UNIFICADA CON HEX]
    Galería de productos que renderiza tarjetas con la lógica de apariencia
    unificada, forzando colores absolutos.
    """
    
    def _render_single_card(post: ProductCardData) -> rx.Component:
        
        # --- ✨ INICIO DE LA LÓGICA DE COLOR UNIFICADA (CORREGIDA) ✨ ---
        
        # 1. Obtiene el tema actual del NAVEGADOR ("light" o "dark")
        site_theme = rx.color_mode_cond("light", "dark")
        
        # 2. Determina la APARIENCIA OBJETIVO ("light" o "dark")
        #    Esta lógica es para los BADGES y el FONDO DE IMAGEN
        #    La apariencia SIEMPRE sigue los toggles que guardó el vendedor.
        card_target_appearance = rx.cond(
            site_theme == "light",
            post.light_mode_appearance, # Si sitio es claro, usa config clara
            post.dark_mode_appearance   # Si sitio es oscuro, usa config oscura
        )
        
        # 3. Determina los colores por DEFECTO basados en la APARIENCIA OBJETIVO (usando HEX)
        default_bg_by_appearance = rx.cond(card_target_appearance == "light", DEFAULT_LIGHT_BG, DEFAULT_DARK_BG)
        default_title_by_appearance = rx.cond(card_target_appearance == "light", DEFAULT_LIGHT_TITLE, DEFAULT_DARK_TITLE)
        default_price_by_appearance = rx.cond(card_target_appearance == "light", DEFAULT_LIGHT_PRICE, DEFAULT_DARK_PRICE)

        # 4. Determina los colores PERSONALIZADOS (Modo Artista)
        #    (Usa el color guardado para el tema actual, o el default de apariencia como fallback)
        custom_bg = rx.cond(
            site_theme == "light",
            post.light_card_bg_color | default_bg_by_appearance,
            post.dark_card_bg_color | default_bg_by_appearance
        )
        custom_title = rx.cond(
            site_theme == "light",
            post.light_title_color | default_title_by_appearance,
            post.dark_title_color | default_title_by_appearance
        )
        custom_price = rx.cond(
            site_theme == "light",
            post.light_price_color | default_price_by_appearance,
            post.dark_price_color | default_price_by_appearance
        )
        
        # 5. Asigna los colores FINALES
        #    Si es "default" (Simple Mode), usa los colores del paso 3.
        #    Si NO es "default" (Artistic Mode), usa los colores del paso 4.
        card_bg_color = rx.cond(post.use_default_style, default_bg_by_appearance, custom_bg)
        title_color = rx.cond(post.use_default_style, default_title_by_appearance, custom_title)
        price_color = rx.cond(post.use_default_style, default_price_by_appearance, custom_price)
        
        # El fondo de la imagen SÍ usa la apariencia simple (con HEX)
        image_bg = rx.cond(
            card_target_appearance == "light",
            DEFAULT_LIGHT_IMAGE_BG,
            DEFAULT_DARK_IMAGE_BG
        )
        
        # --- ✨ FIN DE LA LÓGICA DE COLOR UNIFICADA ✨ ---

        # (La función _card_badge usa card_target_appearance y es correcta)
        def _card_badge(text_content: rx.Var[str], color_scheme: str) -> rx.Component:
            light_colors = {"gray": {"bg": "#F1F3F5", "text": "#495057"}, "violet": {"bg": "#F3F0FF", "text": "#5F3DC4"}, "teal": {"bg": "#E6FCF5", "text": "#0B7285"}}
            dark_colors = {"gray": {"bg": "#373A40", "text": "#ADB5BD"}, "violet": {"bg": "#4D2C7B", "text": "#D0BFFF"}, "teal": {"bg": "#0C3D3F", "text": "#96F2D7"}}
            colors = rx.cond(card_target_appearance == "light", light_colors[color_scheme], dark_colors[color_scheme])
            return rx.box(
                rx.text(text_content, size="2", weight="medium"),
                bg=colors["bg"], color=colors["text"], padding="1px 10px",
                border_radius="var(--radius-full)", font_size="0.8em", white_space="nowrap",
            )

        # --- (Estilos de imagen - SIN CAMBIOS) ---
        image_styles = post.image_styles
        zoom = image_styles.get("zoom", 1.0)
        rotation = image_styles.get("rotation", 0)
        offset_x = image_styles.get("offsetX", 0)
        offset_y = image_styles.get("offsetY", 0)
        transform_style = f"scale({zoom}) rotate({rotation}deg) translateX({offset_x}px) translateY({offset_y}px)"

        # --- Renderizado de la tarjeta (SIN CAMBIOS, AHORA ES CORRECTO) ---
        return rx.box(
            rx.vstack(
                rx.vstack( # Contenedor clickeable
                    rx.box( # Imagen
                         rx.cond(
                            post.main_image_url != "",
                            rx.image(
                                src=rx.get_upload_url(post.main_image_url),
                                width="100%", height="260px", object_fit="contain",
                                transform=transform_style, transition="transform 0.2s ease-out",
                            ),
                            rx.box(rx.icon("image-off", size=48), width="100%", height="260px", bg=rx.color("gray", 3), display="flex", align_items="center", justify_content="center")
                        ),
                         rx.badge( # Origen
                            rx.cond(post.is_imported, "Importado", "Nacional"),
                            color_scheme=rx.cond(post.is_imported, "purple", "cyan"), variant="solid",
                            style={"position": "absolute", "top": "0.5rem", "left": "0.5rem", "z_index": "1"}
                         ),
                        position="relative", width="100%", height="260px", overflow="hidden", bg=image_bg,
                    ),
                    rx.vstack( # Información
                        rx.text(post.title, weight="bold", size="6", width="100%", color=title_color, style=TITLE_CLAMP_STYLE),
                        star_rating_display_safe(post.average_rating, post.rating_count, size=24), 
                         rx.text(post.price_cop, size="5", weight="medium", color=price_color),
                        rx.spacer(),
                        rx.vstack( # Badges envío
                            rx.grid(
                                 _card_badge(post.shipping_display_text, "gray"),
                                rx.cond(
                                    post.is_moda_completa_eligible,
                                    rx.tooltip(_card_badge("Moda Completa", "violet"), content=post.moda_completa_tooltip_text),
                                 ),
                                columns="auto auto", 
                                spacing="2", 
                                align="center", 
                                 justify="start", 
                                width="100%",
                            ),
                            rx.cond(
                                 post.combines_shipping,
                                 rx.tooltip(_card_badge("Envío Combinado", "teal"), content=post.envio_combinado_tooltip_text),
                            ),
                            spacing="1", 
                            align_items="start", 
                             width="100%",
                        ),
                        spacing="2", align_items="start", width="100%", padding="1em", flex_grow="1",
                    ),
                    spacing="0", align_items="stretch", width="100%",
                ),
                 on_click=AppState.open_product_detail_modal(post.id),
                cursor="pointer", height="100%"
            ),
            width="290px", height="480px", bg=card_bg_color,
            border=rx.color_mode_cond("1px solid #e5e5e2", "1px solid #1A1A1A"),
            border_radius="8px", box_shadow="md", overflow="hidden"
        )

    # --- Renderizado de la galería (SIN CAMBIOS) ---
    return rx.cond(
        posts,
        rx.flex(
             rx.foreach(posts, _render_single_card),
            wrap="wrap", spacing="6", justify="center", width="100%", max_width="1800px",
        )
    )