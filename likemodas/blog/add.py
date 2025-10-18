# likemodas/blog/add.py (CORREGIDO)

import reflex as rx
from rx_color_picker.color_picker import color_picker
from likemodas.utils.formatting import format_to_cop
from ..state import AppState, VariantGroupDTO
from ..auth.admin_auth import require_panel_access
from ..models import Category
from ..ui.components import searchable_select
from ..data.product_options import LISTA_COLORES, LISTA_TALLAS_ROPA

def image_selection_grid() -> rx.Component:
    """Muestra las imágenes subidas que aún no han sido agrupadas."""
    return rx.vstack(
        rx.heading("1. Sube y Selecciona Imágenes para Agrupar", size="5"),
        rx.upload(
            rx.vstack(rx.icon("upload", size=32), rx.text("Subir imágenes (máx 5)")),
            id="blog_upload", multiple=True, max_files=5,
            on_drop=AppState.handle_add_upload(rx.upload_files("blog_upload")),
            border="2px dashed var(--gray-a6)", padding="2em", width="100%"
        ),
        rx.cond(
            AppState.uploaded_images,
            rx.vstack(
                rx.flex(
                    rx.foreach(
                        AppState.uploaded_images,
                        lambda img_name: rx.box(
                            rx.image(src=rx.get_upload_url(img_name), width="90px", height="90px", object_fit="cover", border_radius="md"),
                            rx.cond(
                                AppState.image_selection_for_grouping.contains(img_name),
                                rx.box(
                                    # --- ✨ CORRECCIÓN DE ADVERTENCIA: Icono válido "check" ✨ ---
                                    rx.icon("check", color="white", size=24),
                                    bg="rgba(90, 40, 180, 0.7)",
                                    position="absolute", inset="0", border_radius="md",
                                    display="flex", align_items="center", justify_content="center"
                                )
                            ),
                            border="2px solid",
                            border_color=rx.cond(AppState.image_selection_for_grouping.contains(img_name), "var(--violet-9)", "transparent"),
                            border_radius="lg",
                            cursor="pointer",
                            position="relative",
                            on_click=AppState.toggle_image_selection_for_grouping(img_name),
                        )
                    ),
                    wrap="wrap", spacing="3", padding_top="1em",
                ),
                rx.button("Crear Grupo con Imágenes Seleccionadas", on_click=AppState.create_variant_group, margin_top="1em"),
                align_items="start",
            )
        ),
        spacing="3",
        width="100%",
    )

def variant_group_manager() -> rx.Component:
    """Muestra y permite la gestión de los grupos de variantes ya creados."""
    
    # --- ✨ CORRECCIÓN CLAVE: El argumento 'group' ahora tiene un tipo específico ✨ ---
    def render_group_card(group: VariantGroupDTO, index: rx.Var[int]) -> rx.Component:
        is_selected = AppState.selected_group_index == index

        group_attribute_editor = rx.vstack(
            rx.text("Color", size="2", weight="medium"),
            searchable_select(
                placeholder="Seleccionar color...",
                options=AppState.filtered_attr_colores,
                on_change_select=AppState.set_temp_color,
                value_select=AppState.temp_color,
                search_value=AppState.search_attr_color,
                on_change_search=AppState.set_search_attr_color,
                filter_name=f"color_filter_{index}",
            ),
            rx.text("Tallas", size="2", weight="medium"),
            rx.flex(
                rx.foreach(
                    AppState.attr_tallas_ropa,
                    lambda talla: rx.badge(
                        talla,
                        rx.icon("x", size=12, on_click=AppState.remove_variant_attribute("Talla", talla), cursor="pointer"),
                        variant="soft", color_scheme="gray"
                    )
                ),
                wrap="wrap", spacing="2", min_height="28px"
            ),
            rx.hstack(
                rx.select(LISTA_TALLAS_ROPA, placeholder="Añadir talla...", value=AppState.temp_talla, on_change=AppState.set_temp_talla),
                rx.button("Añadir", on_click=AppState.add_variant_attribute("Talla", AppState.temp_talla))
            ),
            rx.button("Guardar Atributos del Grupo", on_click=AppState.update_group_attributes, margin_y="0.5em", size="1", variant="outline"),
            spacing="2", align_items="stretch", width="100%",
        )

        stock_manager_for_group = rx.vstack(
            rx.button("Generar / Actualizar Variantes", on_click=AppState.generate_variants_for_group(index)),
            rx.cond(
                AppState.generated_variants_map.contains(index),
                rx.vstack(
                    rx.foreach(
                        AppState.generated_variants_map[index],
                        lambda variant, var_index: rx.hstack(
                            rx.text(variant.attributes["Talla"]),
                            rx.spacer(),
                            rx.icon_button(rx.icon("minus"), on_click=AppState.decrement_variant_stock(index, var_index), size="1"),
                            rx.input(
                                value=variant.stock.to_string(),
                                on_change=lambda val: AppState.set_variant_stock(index, var_index, val),
                                text_align="center", max_width="50px"
                            ),
                            rx.icon_button(rx.icon("plus"), on_click=AppState.increment_variant_stock(index, var_index), size="1"),
                            align="center"
                        )
                    ),
                    spacing="2", width="100%", padding_top="1em"
                )
            ),
            align_items="stretch", width="100%",
        )

        return rx.card(
            rx.vstack(
                rx.flex(
                    # --- ✨ CORRECCIÓN DE ERROR: Ahora itera sobre una propiedad segura y tipada ✨ ---
                    rx.foreach(
                        group.image_urls,
                        lambda url: rx.image(src=rx.get_upload_url(url), width="60px", height="60px", object_fit="cover", border_radius="sm")
                    ),
                    wrap="wrap", spacing="2",
                ),
                rx.cond(is_selected,
                    rx.vstack(
                        rx.divider(margin_y="1em"),
                        rx.heading("Editar Atributos del Grupo", size="3"),
                        group_attribute_editor,
                        rx.divider(margin_y="1em"),
                        rx.heading("Gestionar Stock de Variantes", size="3"),
                        stock_manager_for_group,
                        align_items="stretch", width="100%", spacing="3"
                    )
                ),
                align_items="stretch",
            ),
            width="100%",
            on_click=AppState.select_group_for_editing(index),
            cursor="pointer",
            border=rx.cond(is_selected, "2px solid var(--violet-9)", "1px solid var(--gray-a6)")
        )

    return rx.vstack(
        rx.heading("2. Gestiona tus Grupos de Variantes", size="5"),
        rx.cond(
            AppState.variant_groups,
            rx.vstack(
                rx.foreach(AppState.variant_groups, render_group_card),
                spacing="4"
            ),
            rx.text("Aún no has creado ningún grupo de variantes.", color_scheme="gray")
        ),
        align_items="stretch",
        spacing="3",
        width="100%",
    )

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
        AppState.variant_groups & (AppState.variant_groups[0].image_urls.length() > 0),
        AppState.variant_groups[0].image_urls[0],
        ""
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
                        rx.text(
                            AppState.price_cop_preview,
                            color=AppState.live_price_color,
                            size="5", weight="medium",
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
    """Página de creación de publicación con la nueva interfaz de grupos."""
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
                display="flex",
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
        padding_left=["0em", "0em", "15em", "15em"],
    )