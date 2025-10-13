# likemodas/blog/add.py (CORREGIDO)

import reflex as rx

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
                    rx.text(
                        rx.cond(AppState.title, AppState.title, "Título del Producto"),
                        weight="bold", size="6", white_space="normal", text_overflow="initial", overflow="visible",
                    ),
                    star_rating_display_safe(0, 0, size=24),
                    rx.text(
                        # ✨ CORRECCIÓN: Ahora lee de AppState.price, que es actualizado por el formulario.
                        format_to_cop(rx.cond(AppState.price, AppState.price.to(float), 0.0)),
                        size="5",
                        weight="medium"
                    ),
                    # --- ✨ INICIO DE LA MODIFICACIÓN DE DISEÑO (IDÉNTICA A LA ANTERIOR) ✨ ---
                    rx.vstack(
                        # Primera fila
                        rx.hstack(
                            rx.badge(
                                AppState.shipping_cost_badge_text_preview,
                                color_scheme="gray", variant="soft", size="2",
                            ),
                            rx.cond(
                                AppState.is_moda_completa,
                                rx.tooltip(
                                    rx.badge("Moda Completa", color_scheme="violet", variant="soft", size="2"),
                                    content=AppState.moda_completa_tooltip_text_preview,
                                ),
                            ),
                            spacing="3", align="center",
                        ),
                        # Segunda fila
                        rx.cond(
                            AppState.combines_shipping,
                            rx.tooltip(
                                rx.badge("Envío Combinado", color_scheme="teal", variant="soft", size="2"),
                                content=AppState.envio_combinado_tooltip_text_preview,
                            ),
                        ),
                        spacing="1", # Espacio vertical
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
        bg=rx.color_mode_cond("#f9f9f9", "#111111"),
        border=rx.color_mode_cond("1px solid #e5e5e5", "1px solid #1a1a1a"),
        border_radius="8px", box_shadow="md", padding="1em",
    )


@require_panel_access # <-- 2. Usa el nuevo decorador
def blog_post_add_content() -> rx.Component:
    """
    Página de creación de publicación con un desplazamiento manual hacia la derecha
    para lograr un centrado visual en PC, sin afectar la vista móvil.
    """
    return rx.hstack(
        rx.grid(
            # Columna del Formulario
            rx.vstack(
                rx.heading("Crear Nueva Publicación", size="7", width="100%", text_align="left", margin_bottom="0.5em"),
                blog_post_add_form(),
                width="100%",
                spacing="4",
            ),
            # Columna de Previsualización
            rx.vstack(
                rx.heading("Previsualización", size="7", width="100%", text_align="left", margin_bottom="0.5em"),
                post_preview(),
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