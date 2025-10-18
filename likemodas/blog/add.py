# likemodas/blog/add.py
# En: likemodas/blog/add.py

# En: likemodas/blog/add.py

import reflex as rx
from rx_color_picker.color_picker import color_picker
from ..state import AppState
from ..auth.admin_auth import require_panel_access
from .forms import blog_post_add_form
from ..ui.components import star_rating_display_safe
from ..utils.formatting import format_to_cop
from reflex.components.component import NoSSRComponent

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

def post_preview() -> rx.Component:
    first_image_url = rx.cond(
        (AppState.variant_groups.length() > 0) & (AppState.variant_groups[0].image_urls.length() > 0),
        AppState.variant_groups[0].image_urls[0],
        ""
    )
    
    return rx.box(
        rx.vstack(
             rx.box(
                rx.image(
                    src=rx.get_upload_url(first_image_url), fallback="/image_off.png", 
                    width="100%", height="100%", object_fit="contain",
                    transform=rx.cond(
                        AppState.is_hydrated,
                        f"scale({AppState.preview_zoom}) rotate({AppState.preview_rotation}deg) translateX({AppState.preview_offset_x}px) translateY({AppState.preview_offset_y}px)",
                        "scale(1)"
                    ),
                    transition="transform 0.2s ease-out",
                ),
                rx.badge(
                    rx.cond(AppState.is_imported, "Importado", "Nacional"),
                    color_scheme=rx.cond(AppState.is_imported, "purple", "cyan"), variant="solid",
                    style={"position": "absolute", "top": "0.5rem", "left": "0.5rem", "z_index": "1"}
                ),
                position="relative", width="100%", height="260px",
                overflow="hidden", 
                border_top_left_radius="var(--radius-3)", border_top_right_radius="var(--radius-3)",
                bg=rx.cond(AppState.card_theme_mode == "light", "white", rx.color("gray", 3)),
             ),
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

@require_panel_access
def blog_post_add_content() -> rx.Component:
    image_editor_panel = rx.vstack(
        rx.divider(margin_y="1em"),
        rx.hstack(
            rx.text("Ajustar Imagen", weight="bold", size="4"),
            rx.spacer(),
            rx.tooltip(
                rx.icon_button(
                    rx.icon("rotate-ccw", size=14),
                    on_click=AppState.reset_image_styles,
                    variant="soft", size="1"
                ),
                content="Resetear ajustes de imagen"
            ),
            width="100%",
            align="center",
        ),
        rx.vstack(
            rx.text("Zoom", size="2"),
            rx.slider(
                value=[AppState.preview_zoom], on_change=AppState.set_preview_zoom, 
                min=0.5, max=3, step=0.05
            ),
            spacing="1", align_items="stretch", width="100%"
        ),
        rx.vstack(
            rx.text("Rotación", size="2"),
            rx.slider(
                value=[AppState.preview_rotation], on_change=AppState.set_preview_rotation, 
                min=-45, max=45, step=1
            ),
            spacing="1", align_items="stretch", width="100%"
        ),
        rx.vstack(
            rx.text("Posición Horizontal (X)", size="2"),
            rx.slider(
                value=[AppState.preview_offset_x], on_change=AppState.set_preview_offset_x, 
                min=-100, max=100, step=1
            ),
            spacing="1", align_items="stretch", width="100%"
        ),
        rx.vstack(
            rx.text("Posición Vertical (Y)", size="2"),
            rx.slider(
                value=[AppState.preview_offset_y], on_change=AppState.set_preview_offset_y, 
                min=-100, max=100, step=1
            ),
            spacing="1", align_items="stretch", width="100%"
        ),
        spacing="3", padding="1em", border="1px dashed var(--gray-a6)",
        border_radius="md", margin_top="1.5em", align_items="stretch",
        width="290px",
    )
    
    return rx.grid(
        rx.vstack(
            rx.heading(
                "Crear Publicación", size="7", width="100%", text_align="left", 
                margin_bottom="0.5em", color_scheme="gray", font_weight="medium"
            ),
            blog_post_add_form(),
            width="100%", spacing="4", align_items="center",
            padding_left={"lg": "15em"}, padding_x=["1em", "2em"],
        ),
        rx.vstack(
            rx.heading("Previsualización", size="7", width="100%", text_align="left", margin_bottom="0.5em"),
            post_preview(),
            rx.vstack( 
                rx.divider(margin_y="1em"),
                rx.text("Personalizar Tarjeta", weight="bold", size="4"),
                rx.text("Puedes guardar un estilo para modo claro y otro para modo oscuro.", size="2", color_scheme="gray"),
                rx.hstack(
                    rx.text("Usar estilo predeterminado del tema", size="3"),
                    rx.spacer(),
                     rx.switch(is_checked=AppState.use_default_style, on_change=AppState.set_use_default_style, size="2"),
                    width="100%", align="center",
                ),
                rx.cond(
                    ~AppState.use_default_style,
                    rx.vstack(
                         rx.segmented_control.root(
                            rx.segmented_control.item("Modo Claro", value="light"),
                            rx.segmented_control.item("Modo Oscuro", value="dark"),
                            on_change=AppState.toggle_preview_mode,
                             value=AppState.card_theme_mode,
                            width="100%",
                        ),
                        rx.popover.root(
                            rx.popover.trigger(
                                 rx.button(rx.hstack(rx.text("Fondo"), rx.spacer(), rx.box(bg=AppState.live_card_bg_color, height="1em", width="1em", border="1px solid var(--gray-a7)", border_radius="var(--radius-2)")), justify="between", width="100%", variant="outline", color_scheme="gray")
                            ),
                            rx.popover.content(color_picker(value=AppState.live_card_bg_color, on_change=AppState.set_live_card_bg_color, variant="classic", size="sm"), padding="0.5em"),
                        ),
                         rx.popover.root(
                            rx.popover.trigger(
                                rx.button(rx.hstack(rx.text("Título"), rx.spacer(), rx.box(bg=AppState.live_title_color, height="1em", width="1em", border="1px solid var(--gray-a7)", border_radius="var(--radius-2)")), justify="between", width="100%", variant="outline", color_scheme="gray")
                            ),
                            rx.popover.content(color_picker(value=AppState.live_title_color, on_change=AppState.set_live_title_color, variant="classic", size="sm"), padding="0.5em"),
                        ),
                        rx.popover.root(
                            rx.popover.trigger(
                                 rx.button(rx.hstack(rx.text("Precio"), rx.spacer(), rx.box(bg=AppState.live_price_color, height="1em", width="1em", border="1px solid var(--gray-a7)", border_radius="var(--radius-2)")), justify="between", width="100%", variant="outline", color_scheme="gray")
                            ),
                            rx.popover.content(color_picker(value=AppState.live_price_color, on_change=AppState.set_live_price_color, variant="classic", size="sm"), padding="0.5em"),
                        ),
                        rx.button("Guardar Personalización", on_click=AppState.save_current_theme_customization, width="100%", margin_top="0.5em"),
                        spacing="3", width="100%", margin_top="1em"
                    ),
                ),
                spacing="3", padding="1em", border="1px dashed var(--gray-a6)",
                border_radius="md", margin_top="1.5em", align_items="stretch",
                width="290px",
            ),
            # Se vuelve a añadir el panel del editor de imagen
            image_editor_panel,
            display={"initial": "none", "lg": "flex"},
            width="100%", spacing="4", position="sticky", top="2em", align_items="center",
        ),
        columns={"initial": "1", "lg": "auto auto"},
        justify="center",
        align="start",
        gap="3em",
        width="100%",
        max_width="1800px",
        padding_y="2em",
        padding_x=["1em", "2em"],
    )