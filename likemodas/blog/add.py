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
    [VERSIÓN FINAL Y ROBUSTA]
    Previsualización que consume texto pre-formateado directamente desde AppState.
    """
    return rx.box(
        rx.vstack(
            rx.vstack(
                rx.box(
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
                    # --- ✨ INICIO DE LA CORRECCIÓN ✨ ---
                    rx.text(
                        rx.cond(AppState.title, AppState.title, "Título del Producto"),
                        weight="bold", size="6", white_space="normal",
                        text_overflow="initial", overflow="visible",
                        # Se aplica el color del estado
                        color=AppState.title_color,
                    ),
                    star_rating_display_safe(0, 0, size=24),
                    rx.text(
                        AppState.price_cop_preview,
                        size="5", weight="medium",
                        # Se aplica el color del estado
                        color=AppState.price_color,
                    ),
                    # --- ✨ INICIO DE LA MODIFICACIÓN DE DISEÑO (IDÉNTICA A LA ANTERIOR) ✨ ---
                    rx.vstack(
                        # Primera fila
                        rx.hstack(
                            rx.badge(
                                AppState.shipping_cost_badge_text_preview,
                                color_scheme="gray", 
                                variant="outline",  # <-- CAMBIO AQUÍ
                                size="2",
                            ),
                            rx.cond(
                                AppState.is_moda_completa,
                                rx.tooltip(
                                    rx.badge(
                                        "Moda Completa", 
                                        color_scheme="violet", 
                                        variant="outline",  # <-- CAMBIO AQUÍ
                                        size="2"
                                    ),
                                    content=AppState.moda_completa_tooltip_text_preview,
                                ),
                            ),
                            spacing="3", align="center",
                        ),
                        # Segunda fila
                        rx.cond(
                            AppState.combines_shipping,
                            rx.tooltip(
                                rx.badge(
                                    "Envío Combinado", 
                                    color_scheme="teal", 
                                    variant="outline",  # <-- CAMBIO AQUÍ
                                    size="2"
                                ),
                                content=AppState.envio_combinado_tooltip_text_preview,
                            ),
                        ),
                        spacing="1",
                        align_items="start",
                    ),
                    # --- ✨ FIN DE LA MODIFICACIÓN DE DISEÑO ✨ ---
                    
                    spacing="1", 
                    align_items="start", 
                    width="100%"
                ),
                spacing="2", width="100%",
            ),
            rx.spacer(),
        ),
        width="290px", height="auto", min_height="450px",
        # ✨ CORRECCIÓN: Usa AppState.card_bg_color en lugar del color por defecto del tema
        bg=AppState.card_bg_color,
        border=rx.color_mode_cond("1px solid #e5e5e5", "1px solid #1a1a1a"),
        border_radius="8px", box_shadow="md", padding="1em",
    )


@require_panel_access # <-- 2. Usa el nuevo decorador
def blog_post_add_content() -> rx.Component:
    """
    Página de creación de publicación con un desplazamiento manual hacia la derecha
    para lograr un centrado visual en PC, sin afectar la vista móvil.
    """
    # --- ✨ INICIO DE LA RESTAURACIÓN ✨ ---
    # Esta es la estructura original que organiza la página en dos columnas.
    return rx.hstack(
        rx.grid(
            # Columna del Formulario (se mantiene igual)
            rx.vstack(
                rx.heading("Crear Nueva Publicación", size="7", width="100%", text_align="left", margin_bottom="0.5em"),
                blog_post_add_form(),
                width="100%",
                spacing="4",
            ),
            
            # Columna de Previsualización (aquí es donde integramos la paleta)
            rx.vstack(
                rx.heading("Previsualización", size="7", width="100%", text_align="left", margin_bottom="0.5em"),
                post_preview(), # Tu componente de previsualización

                # --- El código de la paleta de colores va AQUÍ ---
                rx.vstack(
                    rx.divider(margin_y="1em"),
                    rx.text("Personalizar Tarjeta", weight="bold", size="4"),
                    
                    # Presets de Modo Claro / Oscuro
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
                    
                    # Color Pickers individuales
                    rx.vstack(
                        # Fondo
                        rx.hstack(
                            rx.text("Fondo", flex_grow="1"),
                            # ✨ CORRECCIÓN AQUÍ ✨
                            color_picker(
                                value=AppState.card_bg_color,
                                on_change=AppState.set_card_bg_color,
                            ),
                            align="center", justify="between", width="100%",
                        ),
                        # Título
                        rx.hstack(
                            rx.text("Título", flex_grow="1"),
                            # ✨ CORRECCIÓN AQUÍ ✨
                            color_picker(
                                value=AppState.title_color,
                                on_change=AppState.set_title_color,
                            ),
                            align="center", justify="between", width="100%",
                        ),
                        # Precio
                        rx.hstack(
                            rx.text("Precio", flex_grow="1"),
                            # ✨ CORRECCIÓN AQUÍ ✨
                            color_picker(
                                value=AppState.price_color,
                                on_change=AppState.set_price_color,
                            ),
                            align="center", justify="between", width="100%",
                        ),
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
                # --- Fin del bloque de la paleta de colores ---
                
                display=["none", "none", "flex", "flex"],
                width="100%",
                spacing="4",
                position="sticky",
                top="2em",
            ),
            columns={"initial": "1", "lg": "2fr 1fr"},
            gap="4em",
            width="100%",
            max_width="1800px",
        ),
        width="100%",
        padding_y="2em",
        padding_left=["0em", "0em", "15em", "15em"],
    )
    # --- ✨ FIN DE LA RESTAURACIÓN ✨ ---