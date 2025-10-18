# likemodas/blog/add.py (CORREGIDO)

import reflex as rx
from rx_color_picker.color_picker import color_picker
from ..state import AppState
from ..auth.admin_auth import require_panel_access
from .forms import blog_post_add_form # Importa el formulario restaurado
from ..ui.components import star_rating_display_safe
from ..utils.formatting import format_to_cop

def post_preview() -> rx.Component:
    first_image_url = rx.cond(
        (AppState.variant_groups.length() > 0) & (AppState.variant_groups[0].image_urls.length() > 0),
        AppState.variant_groups[0].image_urls[0],
        ""
    )
    return rx.theme(
        rx.box(
            rx.vstack(
                rx.image(src=rx.get_upload_url(first_image_url), fallback="/image_off.png", width="100%", height="260px", object_fit="cover"),
                rx.vstack(
                    rx.text(rx.cond(AppState.title, AppState.title, "Título del Producto"), color=AppState.live_title_color, weight="bold", size="6"),
                    star_rating_display_safe(0, 0, size=24),
                    rx.text(AppState.price_cop_preview, color=AppState.live_price_color, size="5", weight="medium"),
                    # Puedes añadir los badges de previsualización aquí si lo deseas
                    spacing="1", 
                    align_items="start", 
                    width="100%"
                ),
                spacing="2", width="100%",
                padding="1em"
            ),
            width="290px",
            bg=AppState.live_card_bg_color,
            border="1px solid var(--gray-a6)",
            border_radius="8px", box_shadow="md",
        ),
        appearance=AppState.card_theme_mode,
    )

@require_panel_access
def blog_post_add_content() -> rx.Component:
    """Página de creación de publicación con el diseño original restaurado."""
    return rx.hstack(
        rx.grid(
            rx.vstack(
                rx.heading("Crear Nueva Publicación", size="7", width="100%", text_align="left", margin_bottom="0.5em"),
                blog_post_add_form(),
                width="100%",
                spacing="4",
            ),
            rx.vstack(
                rx.heading("Previsualización", size="7", width="100%", text_align="left", margin_bottom="0.5em"),
                post_preview(),
                # El código para personalizar la tarjeta se mantiene igual
                rx.vstack( 
                    rx.divider(margin_y="1em"),
                    rx.text("Personalizar Tarjeta", weight="bold", size="4"),
                    rx.text("Puedes guardar un estilo para modo claro y otro para modo oscuro.", size="2", color_scheme="gray"),
                    rx.hstack(
                        rx.text("Usar estilo predeterminado del tema", size="3"),
                        rx.spacer(),
                        rx.switch(is_checked=AppState.use_default_style, on_change=AppState.set_use_default_style, size="2"),
                        width="100%",
                        align="center",
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
                    spacing="3",
                    padding="1em",
                    border="1px dashed var(--gray-a6)",
                    border_radius="md",
                    margin_top="1.5em",
                    align_items="stretch",
                    width="290px",
                ),
                display={"initial": "none", "lg": "flex"},
                width="100%",
                spacing="4",
                position="sticky",
                top="2em",
                align_items="center",
            ),
            columns={"initial": "1", "lg": "2fr 1fr"},
            gap="4em",
            width="100%",
            max_width="1800px",
        ),
        width="100%",
        padding_y="2em",
        padding_x=["1em", "2em", "2em", "2em"],
        padding_left={"lg": "15em"},
    )