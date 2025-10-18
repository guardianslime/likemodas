# likemodas/blog/add.py (CORREGIDO)

import reflex as rx
from rx_color_picker.color_picker import color_picker
from ..state import AppState
from ..auth.admin_auth import require_panel_access
from .forms import blog_post_add_form
from ..ui.components import star_rating_display_safe
from ..utils.formatting import format_to_cop

def post_preview() -> rx.Component:
    """
    [VERSIÓN 3.4 FINAL]
    - Título limitado a 2 líneas y con color gris oscuro en modo claro.
    - Contraste sutil añadido al fondo de la tarjeta en modo claro.
    """
    def _preview_badge(text_content: rx.Var[str], color_scheme: str) -> rx.Component:
        light_colors = {
            "gray":   {"bg": "#F1F3F5", "text": "#495057"},
            "violet": {"bg": "#F3F0FF", "text": "#5F3DC4"},
            "teal":   {"bg": "#E6FCF5", "text": "#0B7285"},
        }
        dark_colors = {
            "gray":   {"bg": "#373A40", "text": "#ADB5BD"},
            "violet": {"bg": "#4D2C7B", "text": "#D0BFFF"},
            "teal":   {"bg": "#0C3D3F", "text": "#96F2D7"},
        }
        colors = rx.cond(
            AppState.card_theme_mode == "light",
            light_colors[color_scheme],
            dark_colors[color_scheme],
        )
        return rx.box(
            rx.text(text_content, size="2", weight="medium"),
            bg=colors["bg"], color=colors["text"],
            padding="1px 10px", border_radius="var(--radius-full)", font_size="0.8em",
        )

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
                    width="100%", height="260px", object_fit="contain",
                    border_top_left_radius="var(--radius-3)", border_top_right_radius="var(--radius-3)",
                ),
                rx.badge(
                    rx.cond(AppState.is_imported, "Importado", "Nacional"),
                    color_scheme=rx.cond(AppState.is_imported, "purple", "cyan"), variant="solid",
                    style={"position": "absolute", "top": "0.5rem", "left": "0.5rem", "z_index": "1"}
                ),
                position="relative",
                bg=rx.cond(AppState.card_theme_mode == "light", "white", rx.color("gray", 3)),
            ),
            rx.vstack(
                rx.text(
                    rx.cond(AppState.title, AppState.title, "Título del Producto"), 
                    weight="bold", size="6",
                    no_of_lines=2, # <-- LÍMITE DE DOS LÍNEAS PARA EL TÍTULO
                    color=rx.cond(
                        AppState.use_default_style,
                        # ✨ CORRECCIÓN DE COLOR: De negro a gris oscuro en modo claro ✨
                        rx.cond(AppState.card_theme_mode == "light", rx.color("gray", 12), "white"),
                        AppState.live_title_color,
                    )
                ),
                star_rating_display_safe(0, 0, size=24),
                rx.text(
                    AppState.price_cop_preview, size="5", weight="medium",
                    color=rx.cond(
                        AppState.use_default_style,
                        rx.color("gray", 11),
                        AppState.live_price_color,
                    )
                ),
                rx.spacer(),
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
                        spacing="3", align="center",
                    ),
                    rx.cond(
                        AppState.combines_shipping,
                        rx.tooltip(
                            _preview_badge("Envío Combinado", "teal"),
                            content=AppState.envio_combinado_tooltip_text_preview,
                        ),
                    ),
                    spacing="1", align_items="start", width="100%",
                ),
                spacing="2", align_items="start", width="100%", padding="1em", flex_grow="1",
            ),
            spacing="0", align_items="stretch", height="100%",
        ),
        width="290px", height="480px",
        bg=rx.cond(
            AppState.use_default_style,
            # ✨ CORRECCIÓN DE CONTRASTE: Fondo gris sutil en modo claro ✨
            rx.cond(AppState.card_theme_mode == "light", "#f9f9f9", "var(--gray-2)"),
            AppState.live_card_bg_color
        ),
        border="1px solid var(--gray-a6)",
        border_radius="8px", box_shadow="md",
    )

@require_panel_access
def blog_post_add_content() -> rx.Component:
    return rx.grid(
        rx.vstack(
            rx.heading("Crear Nueva Publicación", size="7", width="100%", text_align="left", margin_bottom="0.5em"),
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
            display={"initial": "none", "lg": "flex"},
            width="100%", spacing="4", position="sticky", top="2em", align_items="center",
        ),
        columns={"initial": "1", "lg": "auto auto"},
        justify="center",
        align="start",
        gap="3em", # Espaciado reducido entre columnas
        width="100%",
        max_width="1800px",
        padding_y="2em",
        padding_x=["1em", "2em"],
    )