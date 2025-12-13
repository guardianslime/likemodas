# En: likemodas/admin/store_components.py (Archivo COMPLETO y CORREGIDO)

import reflex as rx
from ..state import AppState, ProductCardData
# Se importa el componente de estrellas que ya tenías
from ..ui.components import TITLE_CLAMP_STYLE, star_rating_display_safe
# Se importan los colores por defecto para asegurar la consistencia visual
from ..state import (
    DEFAULT_LIGHT_BG, DEFAULT_LIGHT_TITLE, DEFAULT_LIGHT_PRICE,
    DEFAULT_DARK_BG, DEFAULT_DARK_TITLE, DEFAULT_DARK_PRICE,
    # --- ✨ INCLUYE ESTAS CONSTANTES ✨ ---
    DEFAULT_LIGHT_IMAGE_BG, DEFAULT_DARK_IMAGE_BG
)

def admin_product_card(post: ProductCardData) -> rx.Component:
    """
    [VERSIÓN FINAL] Tarjeta de producto para la vista de admin, ahora con el diseño
    y los datos consistentes del resto de la aplicación.
    """
    # 1. (lógica de estilos de imagen sin cambios)
    image_styles = post.image_styles
    zoom = image_styles.get("zoom", 1.0)
    rotation = image_styles.get("rotation", 0)
    offset_x = image_styles.get("offsetX", 0)
    offset_y = image_styles.get("offsetY", 0)
    transform_style = f"scale({zoom}) rotate({rotation}deg) translateX({offset_x}px) translateY({offset_y}px)"

    # --- ✨ INICIO: LÓGICA DE COLOR CORREGIDA ✨ ---
    
    # 1. Obtiene el tema actual del NAVEGADOR ("light" o "dark")
    site_theme = rx.color_mode_cond("light", "dark")
    
    # 2. Determina la APARIENCIA ELEGIDA POR EL VENDEDOR
    seller_chosen_appearance = rx.cond(
        site_theme == "light",
        post.light_mode_appearance, # Si sitio es claro, usa config clara
        post.dark_mode_appearance   # Si sitio es oscuro, usa config oscura
    )
    
    # 3. Aplica la preferencia del USUARIO (el admin)
    # Si 'force_site_theme' es True, usa el 'site_theme'.
    # Si es False, usa el 'seller_chosen_appearance'.
    card_target_appearance = rx.cond(
        AppState.force_site_theme,
        site_theme,
        seller_chosen_appearance
    )
    
    # --- ✨ FIN DE LA LÓGICA DE COLOR CORREGIDA ✨ ---
    
    # El resto de la lógica (colores, badges, etc.) ya depende
    # de 'card_target_appearance', por lo que funcionará automáticamente.

    # 3. Determina los colores por DEFECTO basados en la APARIENCIA OBJETIVO (usando HEX)
    default_bg_by_appearance = rx.cond(card_target_appearance == "light", DEFAULT_LIGHT_BG, DEFAULT_DARK_BG)
    default_title_by_appearance = rx.cond(card_target_appearance == "light", DEFAULT_LIGHT_TITLE, DEFAULT_DARK_TITLE)
    default_price_by_appearance = rx.cond(card_target_appearance == "light", DEFAULT_LIGHT_PRICE, DEFAULT_DARK_PRICE)

    # 4. Determina los colores PERSONALIZADOS (Modo Artista)
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
    card_bg_color = rx.cond(post.use_default_style, default_bg_by_appearance, custom_bg)
    title_color = rx.cond(post.use_default_style, default_title_by_appearance, custom_title)
    price_color = rx.cond(post.use_default_style, default_price_by_appearance, custom_price)
    
    # --- (fondo de imagen) ---
    image_bg = rx.cond(
        card_target_appearance == "light",
        DEFAULT_LIGHT_IMAGE_BG,
        DEFAULT_DARK_IMAGE_BG
    )
    
    # (La función _card_badge es correcta)
    def _card_badge(text_content: rx.Var[str], color_scheme: str) -> rx.Component:
        light_colors = {"gray": {"bg": "#F1F3F5", "text": "#495057"}, "violet": {"bg": "#F3F0FF", "text": "#5F3DC4"}, "teal": {"bg": "#E6FCF5", "text": "#0B7285"}}
        dark_colors = {"gray": {"bg": "#373A40", "text": "#ADB5BD"}, "violet": {"bg": "#4D2C7B", "text": "#D0BFFF"}, "teal": {"bg": "#0C3D3F", "text": "#96F2D7"}}
        colors = rx.cond(card_target_appearance == "light", light_colors[color_scheme], dark_colors[color_scheme])
        return rx.box(
            rx.text(text_content, size="2", weight="medium"),
            bg=colors["bg"], color=colors["text"], padding="1px 10px",
            border_radius="var(--radius-full)", font_size="0.8em", white_space="nowrap",
        )

    
    return rx.box(
        rx.vstack(
            # Contenido visual de la tarjeta
            rx.vstack(
                # Sección de la imagen
                rx.box(
                    rx.cond(
                        post.main_image_url != "",
                        rx.image(
                            src=rx.get_upload_url(post.main_image_url),
                            width="100%", 
                            height="260px",
                            object_fit="contain",
                            transform=transform_style,
                            transition="transform 0.2s ease-out",
                        ),
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
                    bg=image_bg,
                ),
                # Sección de información del producto
                rx.vstack(
                    rx.text(
                        post.title, 
                        weight="bold", 
                        size="6", 
                        width="100%", 
                        color=title_color,
                        style=TITLE_CLAMP_STYLE
                    ),
                    star_rating_display_safe(post.average_rating, post.rating_count, size=24),
                    rx.text(post.price_cop, size="5", weight="medium", color=price_color),
                    rx.spacer(),
                    rx.vstack(
                        rx.grid( # <-- Usamos grid para alinear
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
                            post.combines_shipping,  # <--- VOLVEMOS A ESTO (Variable directa)
                            rx.tooltip(_card_badge("Envío Combinado", "teal"), content=post.envio_combinado_tooltip_text),
                        ),
                        spacing="1", align_items="start", width="100%",
                    ),
                    spacing="2", align_items="start", width="100%", padding="1em", flex_grow="1",
                ),
                spacing="0", align_items="stretch", width="100%",
            ),
            rx.spacer(),
            # Botón de acción específico para el panel de administrador
            rx.button(
                "Editar / Ver Detalles",
                on_click=AppState.start_editing_post(post.id),
                width="100%",
                variant="outline",
                color_scheme="violet"
            ),
            align="center", spacing="3", height="100%"
        ),
        width="290px",
        height="480px", # Altura unificada con la previsualización
        bg=card_bg_color,
        border=rx.color_mode_cond("1px solid #e5e5e5", "1px solid #1a1a1a"),
        border_radius="8px",
        box_shadow="md",
        overflow="hidden"
    )

def admin_store_gallery_component(posts: rx.Var[list[ProductCardData]]) -> rx.Component:
    """
    Galería de productos para administradores que utiliza la tarjeta unificada.
    """
    return rx.flex(
        rx.foreach(
            posts,
            admin_product_card,
        ),
        wrap="wrap", spacing="6", justify="center", width="100%", max_width="1800px",
    )