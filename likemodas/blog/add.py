# likemodas/blog/add.py (CORREGIDO)

import reflex as rx

# --- ✨ 1. AÑADE ESTA LÍNEA DE IMPORTACIÓN AL INICIO DEL ARCHIVO ✨ ---
from rx_color_picker.color_picker import color_picker
# --- ✨ FIN DEL CAMBIO ✨ ---
from likemodas.utils.formatting import format_to_cop
from ..auth.admin_auth import require_panel_access # <-- 1. Importa el decorador correcto
from .forms import blog_post_add_form
from ..blog.state import BlogAdminState
from ..state import AppState
from ..ui.skeletons import skeleton_post_preview
from ..ui.components import star_rating_display_safe

def post_preview() -> rx.Component:
    """
    [VERSIÓN FINAL CON BADGES 100% PERSONALIZADOS Y FIELES A LA TIENDA]
    """
    
    # --- ✨ INICIO: NUEVA FUNCIÓN PARA CONSTRUIR BADGES MANUALMENTE ✨ ---
    def _preview_badge(text_content: rx.Var[str], color_scheme: str) -> rx.Component:
        """
        Construye un badge desde cero usando rx.box para un control total del estilo.
        """
        # Paleta de colores EXACTA para MODO CLARO (imitando la tienda)
        light_colors = {
            "gray":   {"bg": "#F1F3F5", "text": "#495057"},
            "violet": {"bg": "#F3F0FF", "text": "#5F3DC4"},
            "teal":   {"bg": "#E6FCF5", "text": "#0B7285"},
        }

        # Paleta de colores EXACTA para MODO OSCURO (imitando la tienda)
        dark_colors = {
            "gray":   {"bg": "#373A40", "text": "#ADB5BD"},
            "violet": {"bg": "#4D2C7B", "text": "#D0BFFF"},
            "teal":   {"bg": "#0C3D3F", "text": "#96F2D7"},
        }
        
        # Selecciona la paleta correcta según el modo de la tarjeta
        colors = rx.cond(
            AppState.card_theme_mode == "light",
            light_colors[color_scheme],
            dark_colors[color_scheme],
        )

        return rx.box(
            rx.text(text_content, size="2", weight="medium"),
            bg=colors["bg"],
            color=colors["text"],
            padding="1px 10px", # Padding vertical y horizontal para la apariencia de badge
            border_radius="var(--radius-full)",
            font_size="0.8em",
        )
    # --- ✨ FIN DE LA FUNCIÓN AUXILIAR ✨ ---

    return rx.theme(
        rx.box(
            rx.vstack(
                rx.vstack(
                    rx.box(
                        # ... (código de la imagen del producto se mantiene igual)
                        rx.cond(
                            AppState.new_variants,
                            rx.image(src=rx.get_upload_url(AppState.new_variants[0].get("image_url", "")), width="100%", height="260px", object_fit="cover"),
                            rx.box(rx.icon("image_off", size=48), width="100%", height="260px", bg=rx.color("gray", 3), display="flex", align_items="center", justify_content="center")
                        ),
                        rx.badge(
                            rx.cond(AppState.is_imported, "Importado", "Nacional"),
                            color_scheme=rx.cond(AppState.is_imported, "purple", "cyan"),
                            variant="solid",
                            style={"position": "absolute", "top": "0.5rem", "left": "0.5rem", "z_index": "1"}
                        ),
                        position="relative", width="260px", height="260px",
                    ),
                    rx.vstack(
                        rx.text(
                            rx.cond(AppState.title, AppState.title, "Título del Producto"),
                            color=AppState.title_color,
                            weight="bold", size="6", white_space="normal", text_overflow="initial", overflow="visible",
                        ),
                        star_rating_display_safe(0, 0, size=24),
                        rx.text(
                            AppState.price_cop_preview,
                            color=AppState.price_color,
                            size="5", weight="medium",
                        ),
                        
                        # --- Uso de la nueva función _preview_badge ---
                        rx.vstack(
                            rx.hstack(
                                _preview_badge(AppState.shipping_cost_badge_text_preview, "gray"),
                                rx.cond(
                                    AppState.is_moda_completa,
                                    rx.tooltip(
                                        _preview_badge("Moda Completa", "violet"),
                                        content=AppState.moda_completa_tooltip_text_preview,
                                    ),
                                ),
                                spacing="3",
                                align="center",
                            ),
                            rx.cond(
                                AppState.combines_shipping,
                                rx.tooltip(
                                    _preview_badge("Envío Combinado", "teal"),
                                    content=AppState.envio_combinado_tooltip_text_preview,
                                ),
                            ),
                            spacing="1",
                            align_items="start",
                        ),
                        spacing="1", 
                        align_items="start", 
                        width="100%"
                    ),
                    spacing="2", width="100%",
                ),
                rx.spacer(),
            ),
            width="290px", height="auto", min_height="450px",
            bg=AppState.card_bg_color,
            border="1px solid var(--gray-a6)",
            border_radius="8px", box_shadow="md", padding="1em",
        ),
        appearance=AppState.card_theme_mode,
    )


@require_panel_access
def blog_post_add_content() -> rx.Component:
    """
    Página de creación de publicación con previsualización visible en móvil
    y sección de personalización rediseñada.
    """
    return rx.hstack(
        rx.grid(
            # Columna del Formulario (sin cambios)
            rx.vstack(
                rx.heading("Crear Nueva Publicación", size="7", width="100%", text_align="left", margin_bottom="0.5em"),
                blog_post_add_form(),
                width="100%",
                spacing="4",
            ),
            
            # Columna de Previsualización (con correcciones)
            rx.vstack(
                rx.heading("Previsualización", size="7", width="100%", text_align="left", margin_bottom="0.5em"),
                post_preview(),

                # --- ✨ INICIO: SECCIÓN DE PERSONALIZACIÓN REDISEÑADA ✨ ---
                rx.vstack(
                    rx.divider(margin_y="1em"),
                    rx.text("Personalizar Tarjeta", weight="bold", size="4"),
                    
                    # Presets de Modo Claro / Oscuro (sin cambios)
                    rx.segmented_control.root(
                        rx.segmented_control.item("Modo Claro", value="light"),
                        rx.segmented_control.item("Modo Oscuro", value="dark"),
                        on_change=lambda mode: rx.cond(
                            mode == "light",
                            AppState.apply_light_theme_preset(),
                            AppState.apply_dark_theme_preset()
                        ),
                        default_value="light",
                        width="100%",
                    ),
                    
                    # Cuadrícula para alinear los Color Pickers
                    rx.grid(
                        # Fila 1: Fondo
                        rx.text("Fondo", size="2", align_self="center"),
                        color_picker(
                            value=AppState.card_bg_color,
                            on_change=AppState.set_card_bg_color,
                            size="sm", # Tamaño más pequeño y estético
                        ),

                        # Fila 2: Título
                        rx.text("Título", size="2", align_self="center"),
                        color_picker(
                            value=AppState.title_color,
                            on_change=AppState.set_title_color,
                            size="sm",
                        ),

                        # Fila 3: Precio
                        rx.text("Precio", size="2", align_self="center"),
                        color_picker(
                            value=AppState.price_color,
                            on_change=AppState.set_price_color,
                            size="sm",
                        ),
                        
                        columns="2", # Dos columnas: una para el texto, una para el picker
                        spacing="3",
                        width="100%",
                        margin_top="1em"
                    ),
                    
                    spacing="3",
                    padding="1em",
                    border="1px dashed var(--gray-a6)",
                    border_radius="md",
                    margin_top="1.5em",
                    align_items="stretch",
                    width="100%",
                ),
                # --- ✨ FIN: SECCIÓN REDISEÑADA ✨ ---
                
                # --- ✨ CORRECCIÓN PARA VISIBILIDAD MÓVIL ✨ ---
                # Antes: display=["none", "none", "flex", "flex"]
                # Ahora: display="flex" para que siempre se muestre.
                display="flex",
                
                width="100%",
                spacing="4",
                position="sticky",
                top="2em",
            ),
            # El grid principal se encarga de apilar las columnas en móvil
            columns={"initial": "1", "lg": "2fr 1fr"},
            gap="4em",
            width="100%",
            max_width="1800px",
        ),
        width="100%",
        padding_y="2em",
        padding_left=["0em", "0em", "15em", "15em"],
    )