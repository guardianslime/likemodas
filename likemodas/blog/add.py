# likemodas/blog/add.py
# En: likemodas/blog/add.py

import reflex as rx
from rx_color_picker.color_picker import color_picker
from ..state import AppState
from ..auth.admin_auth import require_panel_access
from .forms import blog_post_add_form
from ..ui.components import star_rating_display_safe
from ..utils.formatting import format_to_cop
from typing import Dict, Any
from reflex.components.component import NoSSRComponent
import json # Importa la librería json

# --- ✨ INICIO: NUEVO COMPONENTE AUTOCONTENIDO PARA IMAGEN INTERACTIVA ✨ ---
class Moveable(NoSSRComponent):
    """Componente Reflex que envuelve la librería React-Moveable."""
    library = "react-moveable"
    tag = "Moveable"
    target: rx.Var[str]
    draggable: rx.Var[bool] = True
    resizable: rx.Var[bool] = True
    rotatable: rx.Var[bool] = True
    snappable: rx.Var[bool] = True
    keep_ratio: rx.Var[bool] = False
    on_drag_end: rx.EventHandler[lambda e: [e]]
    on_resize_end: rx.EventHandler[lambda e: [e]]
    on_rotate_end: rx.EventHandler[lambda e: [e]]
    def _get_custom_code(self) -> str:
        return """
const onDragEnd = (e, on_drag_end) => {
    if (on_drag_end) { on_drag_end({transform: e.lastEvent.transform}); }
    return e;
}
const onResizeEnd = (e, on_resize_end) => {
    if (on_resize_end) { on_resize_end({transform: e.lastEvent.transform}); }
    return e;
}
const onRotateEnd = (e, on_rotate_end) => {
    if (on_rotate_end) { on_rotate_end({transform: e.lastEvent.transform}); }
    return e;
}
"""
moveable = Moveable.create


def post_preview() -> rx.Component:
    """
    [VERSIÓN FINAL CORREGIDA]
    - Resuelve el error de React #306 al renderizar Moveable condicionalmente.
    """
    first_image_url = rx.cond(
        (AppState.variant_groups.length() > 0) & (AppState.variant_groups[0].image_urls.length() > 0),
        AppState.variant_groups[0].image_urls[0],
        ""
    )
    
    return rx.box(
        rx.vstack(
            rx.box(
                rx.box(
                    rx.image(
                        src=rx.get_upload_url(first_image_url),
                        fallback="/image_off.png",
                        id="moveable_target_image",
                        width="100%", height="100%",
                        object_fit="contain",
                        transform=AppState.preview_image_transform,
                    ),
                    # --- ✨ INICIO: CORRECCIÓN CLAVE ✨ ---
                    # El componente Moveable ahora solo se renderiza si 'first_image_url' no es una cadena vacía.
                    # Esto evita que se inicie sin tener un objetivo al cual acoplarse.
                    rx.cond(
                        first_image_url,
                        moveable(
                            target="#moveable_target_image",
                            keep_ratio=True,
                            on_drag_end=AppState.set_preview_image_transform,
                            on_resize_end=AppState.set_preview_image_transform,
                            on_rotate_end=AppState.set_preview_image_transform,
                        )
                    ),
                    # --- ✨ FIN: CORRECCIÓN CLAVE ✨ ---
                    width="100%", height="260px",
                    overflow="hidden",
                    border_top_left_radius="var(--radius-3)", border_top_right_radius="var(--radius-3)",
                    bg=rx.cond(AppState.card_theme_mode == "light", "white", rx.color("gray", 3)),
                ),
                rx.badge(
                    rx.cond(AppState.is_imported, "Importado", "Nacional"),
                    color_scheme=rx.cond(AppState.is_imported, "purple", "cyan"), variant="solid",
                    style={"position": "absolute", "top": "0.5rem", "left": "0.5rem", "z_index": "2"}
                ),
                position="relative",
            ),
            # El resto del código de la tarjeta (título, precio, etc.) no cambia
            rx.vstack(
                rx.text(
                    rx.cond(AppState.title, AppState.title, "Título del Producto"), 
                    weight="bold", size="6", no_of_lines=2, width="100%",
                    color=rx.cond(
                        AppState.use_default_style,
                        rx.cond(AppState.card_theme_mode == "light", rx.color("gray", 11), "white"),
                        AppState.live_title_color,
                    )
                ),
                star_rating_display_safe(0, 0, size=24),
                rx.text(
                    AppState.price_cop_preview, size="5", weight="medium",
                    color=rx.cond(
                         AppState.use_default_style,
                        rx.cond(AppState.card_theme_mode == "light", rx.color("gray", 9), rx.color("gray", 11)),
                        AppState.live_price_color,
                    )
                ),
                rx.spacer(),
                # Aquí irían los badges de envío si los tuvieras definidos en una función
                spacing="2", align_items="start", width="100%", padding="1em", flex_grow="1",
            ),
            spacing="0", align_items="stretch", height="100%",
        ),
        width="290px", height="480px",
        bg=rx.cond(
             AppState.use_default_style,
            rx.cond(AppState.card_theme_mode == "light", "#fdfcff", "var(--gray-2)"),
            AppState.live_card_bg_color
        ),
        border="1px solid var(--gray-a6)",
        border_radius="8px", box_shadow="md",
    )