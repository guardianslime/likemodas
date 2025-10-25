# En: likemodas/admin/store_components.py (CORREGIDO Y UNIFICADO)

import reflex as rx
from ..state import AppState, ProductCardData
# Se importa el componente de estrellas que ya tenías
from ..ui.components import TITLE_CLAMP_STYLE, star_rating_display_safe
# Se importan los colores por defecto para asegurar la consistencia visual
from ..state import (
    DEFAULT_LIGHT_BG, DEFAULT_LIGHT_TITLE, DEFAULT_LIGHT_PRICE,
    DEFAULT_DARK_BG, DEFAULT_DARK_TITLE, DEFAULT_DARK_PRICE
)

def admin_product_card(post: ProductCardData) -> rx.Component:
    """
    [VERSIÓN FINAL] Tarjeta de producto para la vista de admin, ahora con el diseño
    y los datos consistentes del resto de la aplicación.
    """
    # 1. Obtiene los estilos de imagen guardados (zoom, rotación, etc.)
    image_styles = post.image_styles
    zoom = image_styles.get("zoom", 1.0)
    rotation = image_styles.get("rotation", 0)
    offset_x = image_styles.get("offsetX", 0)
    offset_y = image_styles.get("offsetY", 0)
    transform_style = f"scale({zoom}) rotate({rotation}deg) translateX({offset_x}px) translateY({offset_y}px)"

    # 2. Lógica de colores idéntica a la tarjeta pública para total consistencia
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
            # Contenido visual de la tarjeta
            rx.vstack(
                # Sección de la imagen
                rx.box(
                    rx.cond(
                        post.main_image_url != "",
                        rx.image(
                            src=rx.get_upload_url(post.main_image_url),
                            width="100%", height="260px",
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
                    bg=rx.color_mode_cond("white", rx.color("gray", 3)),
                ),
                # Sección de información del producto
                rx.vstack(
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