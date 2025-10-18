# likemodas/blog/add.py (CORREGIDO)

import reflex as rx
from rx_color_picker.color_picker import color_picker
from likemodas.blog.forms import image_selection_grid, variant_group_manager
from likemodas.utils.formatting import format_to_cop
from ..state import AppState, VariantGroupDTO
from ..auth.admin_auth import require_panel_access
from ..models import Category
from ..ui.components import searchable_select, star_rating_display_safe
from ..data.product_options import LISTA_COLORES, LISTA_TALLAS_ROPA

def blog_post_add_form() -> rx.Component:
    """Formulario rediseñado para la creación de productos con grupos de variantes."""
    return rx.form(
        rx.vstack(
            rx.heading("Datos Generales del Producto", size="5"),
            rx.vstack(
                rx.text("Título del Producto"),
                rx.input(name="title", on_change=AppState.set_title, required=True),
                rx.text("Categoría"),
                rx.select(AppState.categories, on_change=AppState.set_category, name="category", required=True),
                rx.grid(
                    rx.vstack(rx.text("Precio (COP)"), rx.input(name="price", on_change=AppState.set_price, type="number", required=True)),
                    rx.vstack(rx.text("Ganancia (COP)"), rx.input(name="profit", value=AppState.profit_str, on_change=AppState.set_profit_str, type="number")),
                    columns="2", 
                    spacing="4"
                ),
                rx.text("Descripción"),
                rx.text_area(name="content", on_change=AppState.set_content, style={"height": "120px"}),
                spacing="3", align_items="stretch"
            ),
            rx.divider(margin_y="2em"),
            image_selection_grid(),
            rx.divider(margin_y="2em"),
            variant_group_manager(),
            rx.divider(margin_y="2em"),
            rx.hstack(
                rx.button("Publicar Producto", type="submit", color_scheme="violet", size="3"),
                width="100%", justify="end",
            ),
            spacing="5", 
            width="100%",
        ),
        on_submit=AppState.submit_and_publish,
        reset_on_submit=True,
    )

def post_preview() -> rx.Component:
    """Previsualización del producto que muestra la primera imagen del primer grupo."""
    
    first_image_url = rx.cond(
        (AppState.variant_groups.length() > 0) & (AppState.variant_groups[0].image_urls.length() > 0),
        AppState.variant_groups[0].image_urls[0],
        ""
    )

    # Función interna para recrear los badges con el estilo correcto
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

    return rx.theme(
        rx.box(
            rx.vstack(
                rx.vstack(
                    rx.box(
                        rx.cond(
                            first_image_url != "",
                            rx.image(src=rx.get_upload_url(first_image_url), width="100%", height="260px", object_fit="cover"),
                            rx.box(rx.icon("image-off", size=48), width="100%", height="260px", bg=rx.color("gray", 3), display="flex", align_items="center", justify_content="center")
                        ),
                        position="relative", width="260px", height="260px",
                    ),
                    rx.vstack(
                        rx.text(
                            rx.cond(AppState.title, AppState.title, "Título del Producto"),
                            color=AppState.live_title_color,
                            weight="bold", size="6",
                        ),
                        star_rating_display_safe(0, 0, size=24), # Estrellas restauradas
                        rx.text(
                            AppState.price_cop_preview,
                            color=AppState.live_price_color,
                            size="5", weight="medium",
                        ),
                        # Badges restaurados
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
                            spacing="1", align_items="start",
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
            bg=AppState.live_card_bg_color,
            border="1px solid var(--gray-a6)",
            border_radius="8px", box_shadow="md", padding="1em",
        ),
        appearance=AppState.card_theme_mode,
    )


@require_panel_access
def blog_post_add_content() -> rx.Component:
    """Página de creación de publicación con la nueva interfaz de grupos y el diseño original."""
    return rx.hstack(
        rx.grid(
            rx.vstack(
                rx.heading("Crear Nueva Publicación", size="7", width="100%", text_align="left", margin_bottom="0.5em"),
                blog_post_add_form(), # Llama al formulario restaurado
                width="100%",
                spacing="4",
            ),
            rx.vstack(
                rx.heading("Previsualización", size="7", width="100%", text_align="left", margin_bottom="0.5em"),
                post_preview(),
                
                # --- ✨ INICIO: SECCIÓN DE PERSONALIZACIÓN COMPLETA ✨ ---
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
                                    rx.button(
                                        rx.hstack(
                                            rx.text("Fondo"), rx.spacer(),
                                            rx.box(bg=AppState.live_card_bg_color, height="1em", width="1em", border="1px solid var(--gray-a7)", border_radius="var(--radius-2)"),
                                        ),
                                        justify="between", width="100%", variant="outline", color_scheme="gray",
                                    )
                                ),
                                rx.popover.content(
                                    color_picker(
                                        value=AppState.live_card_bg_color,
                                        on_change=AppState.set_live_card_bg_color,
                                        variant="classic", size="sm",
                                    ),
                                    padding="0.5em",
                                ),
                            ),
                            rx.popover.root(
                                rx.popover.trigger(
                                    rx.button(
                                        rx.hstack(
                                            rx.text("Título"), rx.spacer(),
                                            rx.box(bg=AppState.live_title_color, height="1em", width="1em", border="1px solid var(--gray-a7)", border_radius="var(--radius-2)"),
                                        ),
                                        justify="between", width="100%", variant="outline", color_scheme="gray",
                                    )
                                ),
                                rx.popover.content(
                                    color_picker(
                                        value=AppState.live_title_color,
                                        on_change=AppState.set_live_title_color,
                                        variant="classic", size="sm",
                                    ),
                                    padding="0.5em",
                                ),
                            ),
                            rx.popover.root(
                                rx.popover.trigger(
                                    rx.button(
                                        rx.hstack(
                                            rx.text("Precio"), rx.spacer(),
                                            rx.box(bg=AppState.live_price_color, height="1em", width="1em", border="1px solid var(--gray-a7)", border_radius="var(--radius-2)"),
                                        ),
                                        justify="between", width="100%", variant="outline", color_scheme="gray",
                                    )
                                ),
                                rx.popover.content(
                                    color_picker(
                                        value=AppState.live_price_color,
                                        on_change=AppState.set_live_price_color,
                                        variant="classic", size="sm",
                                    ),
                                    padding="0.5em",
                                ),
                            ),
                            rx.button(
                                "Guardar Personalización",
                                on_click=AppState.save_current_theme_customization,
                                width="100%",
                                margin_top="0.5em"
                            ),
                            spacing="3",
                            width="100%",
                            margin_top="1em"
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
                # --- ✨ FIN DE LA SECCIÓN DE PERSONALIZACIÓN ✨ ---
                display={"initial": "none", "lg": "flex"}, # Oculta la previsualización en pantallas pequeñas
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
        padding_left=["1em", "2em", "15em", "15em"],
        padding_right=["1em", "2em"],
    )