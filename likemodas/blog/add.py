# likemodas/blog/add.py
# En: likemodas/blog/add.py

# En: likemodas/blog/add.py

import reflex as rx
from rx_color_picker.color_picker import color_picker

from likemodas.data.product_options import LISTA_TALLAS_ROPA
from ..state import AppState, VariantGroupDTO
from ..auth.admin_auth import require_panel_access
from .forms import blog_post_add_form
from ..ui.components import TITLE_CLAMP_STYLE, searchable_select, star_rating_display_safe
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


# --- Componente del formulario (antes en forms.py) ---
def blog_post_add_form() -> rx.Component:
    """
    Formulario completo para AÑADIR una nueva publicación, con la sintaxis
    de los manejadores de eventos corregida para evitar AttributeErrors.
    """
    def image_and_group_section() -> rx.Component:
        def render_group_card(group: VariantGroupDTO, index: rx.Var[int]) -> rx.Component:
            is_selected = AppState.selected_group_index == index
            return rx.box(
                rx.flex(
                    rx.foreach(
                        group.image_urls,
                        lambda url: rx.image(src=rx.get_upload_url(url), width="40px", height="40px", object_fit="cover", border_radius="sm")
                    ),
                    wrap="wrap", spacing="2",
                ),
                rx.icon(
                    "trash-2",
                    # ✨ CORRECCIÓN (lambda): Envolver la llamada
                    on_click=lambda: AppState.remove_variant_group(index),
                    style={
                        "position": "absolute", "top": "-8px", "right": "-8px",
                        "background": "var(--red-9)", "color": "white",
                        "border_radius": "50%", "padding": "2px", "cursor": "pointer",
                        "width": "20px", "height": "20px"
                    }
                ),
                position="relative",
                border_width="2px",
                border_color=rx.cond(is_selected, "var(--violet-9)", "transparent"),
                padding="0.25em", border_radius="md", cursor="pointer",
                # ✨ CORRECCIÓN (lambda): Envolver la llamada
                on_click=lambda: AppState.select_group_for_editing(index),
            )

        return rx.vstack(
            rx.text("1. Subir Imágenes (máx 10)", weight="bold"),
            rx.upload(
                 rx.vstack(rx.icon("upload"), rx.text("Arrastra o haz clic")),
                id="blog_upload", multiple=True, max_files=10,
                on_drop=AppState.handle_add_upload(rx.upload_files("blog_upload")),
                border="1px dashed var(--gray-a6)", padding="2em", width="100%"
            ),
            rx.text("2. Selecciona y ordena las imágenes para el grupo:"),
            rx.flex(
                 rx.foreach(
                    AppState.uploaded_images,
                    lambda img_name: rx.box(
                        rx.image(src=rx.get_upload_url(img_name), width="80px", height="80px", object_fit="cover", border_radius="md"),
                        rx.cond(
                            AppState.image_selection_for_grouping.contains(img_name),
                            rx.box(
                                rx.text(AppState.selection_order_map[img_name], color="white", weight="bold", font_size="1.5em"),
                                # ✨ ESTE ES EL HSTACK QUE HEMOS ELIMINADO COMPLETAMENTE ✨
                                # (Antes: rx.hstack con flechas)
                                # ¡Ya no está aquí!
                                bg="rgba(90, 40, 180, 0.75)", position="absolute", inset="0", border_radius="md",
                                display="flex", align_items="center", justify_content="center"
                            )
                        ),
                        rx.icon("x", on_click=lambda: AppState.remove_uploaded_image(img_name),
                            style={"position": "absolute", "top": "-6px", "right": "-6px", "background": "var(--red-9)", "color": "white", "border_radius": "50%", "padding": "2px", "cursor": "pointer", "width": "18px", "height": "18px"}
                        ),
                        position="relative", border="2px solid",
                        border_color=rx.cond(AppState.image_selection_for_grouping.contains(img_name), "var(--violet-9)", "transparent"),
                        border_radius="lg", cursor="pointer",
                        on_click=lambda: AppState.toggle_image_selection_for_grouping(img_name),
                    )
                ),
                wrap="wrap", spacing="3", padding_top="0.5em",
             ),
            rx.button("Crear Grupo de Color", on_click=AppState.create_variant_group, margin_top="0.5em", width="100%", type="button"),
            rx.divider(margin_y="1em"),
            rx.text("3. Grupos (Selecciona uno para editar abajo):"),
            rx.flex(rx.foreach(AppState.variant_groups, render_group_card), wrap="wrap", spacing="2"),
            spacing="3", width="100%", align_items="stretch",
        )

    def attributes_and_stock_section() -> rx.Component:
        return rx.cond(
             AppState.selected_group_index >= 0,
            rx.vstack(
                rx.divider(margin_y="1.5em"),
                rx.heading(f"4. Características y Stock para Grupo #{AppState.selected_group_index + 1}", size="5"),
                rx.grid(
                    rx.vstack(
                        rx.text("Atributos del Grupo", weight="medium"),
                        rx.text("Color"),
                        searchable_select(
                            placeholder="Seleccionar color...", options=AppState.filtered_attr_colores,
                            on_change_select=AppState.set_temp_color, value_select=AppState.temp_color,
                            search_value=AppState.search_attr_color, on_change_search=AppState.set_search_attr_color,
                            filter_name="color_filter_main",
                        ),
                        rx.text("Talla"),
                        rx.hstack(
                            rx.select(LISTA_TALLAS_ROPA, placeholder="Añadir talla...", value=AppState.temp_talla, on_change=AppState.set_temp_talla),
                            # ✨ CORRECCIÓN (lambda) ✨
                            rx.button("Añadir", on_click=lambda: AppState.add_variant_attribute("Talla", AppState.temp_talla), type="button")
                        ),
                        rx.flex(
                             rx.foreach(
                                AppState.attr_tallas_ropa,
                                # ✨ CORRECCIÓN (lambda) ✨
                                lambda talla: rx.badge(talla, rx.icon("x", size=12, on_click=lambda: AppState.remove_variant_attribute("Talla", talla), cursor="pointer"), variant="soft", color_scheme="gray")
                             ),
                            wrap="wrap", spacing="2", min_height="28px", padding_top="0.5em"
                        ),
                        rx.button("Guardar Atributos", on_click=AppState.update_group_attributes, margin_top="1em", size="2", variant="outline", type="button"),
                        spacing="3", align_items="stretch",
                     ),
                    rx.vstack(
                        rx.text("Variantes y Stock", weight="medium"),
                        # ✨ CORRECCIÓN (lambda) ✨
                        rx.button("Generar / Actualizar Variantes", on_click=lambda: AppState.generate_variants_for_group(AppState.selected_group_index), type="button"),
                        rx.cond(
                            AppState.generated_variants_map.contains(AppState.selected_group_index),
                            rx.scroll_area(
                                rx.vstack(
                                     rx.foreach(
                                        AppState.generated_variants_map[AppState.selected_group_index],
                                        lambda variant, var_index: rx.hstack(
                                            rx.text(variant.attributes["Talla"]), rx.spacer(),
                                            # ✨ CORRECCIÓN (lambda) ✨
                                            rx.icon_button(rx.icon("minus"), on_click=lambda: AppState.decrement_variant_stock(AppState.selected_group_index, var_index), size="1", type="button"),
                                            rx.input(value=variant.stock.to_string(), on_change=lambda val: AppState.set_variant_stock(AppState.selected_group_index, var_index, val), text_align="center", max_width="50px"),
                                            rx.icon_button(rx.icon("plus"), on_click=lambda: AppState.increment_variant_stock(AppState.selected_group_index, var_index), size="1", type="button"),
                                            align="center"
                                         )
                                    ),
                                    spacing="2", width="100%", padding_top="1em"
                                 ),
                                max_height="200px", type="auto", scrollbars="vertical"
                            )
                        ),
                         spacing="3", align_items="stretch",
                    ),
                    columns="2", spacing="4", width="100%"
                ),
                align_items="stretch", width="100%"
            )
        )

    return rx.vstack(
        rx.grid(
            rx.vstack(
                image_and_group_section(),
                attributes_and_stock_section(),
                spacing="5",
                width="100%",
            ),
            rx.vstack(
                rx.vstack(
                    rx.text("Título del Producto"), 
                    rx.input(
                        name="title", 
                        value=AppState.title, 
                        on_change=AppState.set_title, 
                        required=True, 
                        max_length=40  # <--- CORRECCIÓN AÑADIDA
                    ), 
                    align_items="stretch"
                ),
                rx.vstack(rx.text("Categoría"), rx.select(AppState.categories, value=AppState.category, on_change=AppState.set_category, name="category", required=True), align_items="stretch"),
                rx.grid(
                    rx.vstack(rx.text("Precio (COP)"), rx.input(
                        name="price", 
                        value=AppState.price_str, 
                        on_change=AppState.set_price_str, # <--- Asegúrate que sea este
                        type="number", 
                        required=True, 
                        placeholder="Ej: 55000"
                    )),
                    # Campo de Ganancia
                    rx.vstack(rx.text("Ganancia (COP)"), rx.input(
                        name="profit", 
                        value=AppState.profit_str, 
                        on_change=AppState.set_profit_str,
                        type="number", 
                        placeholder="Ej: 15000",
                        # --- ✨ INICIO: LÍMITE DE DÍGITOS DINÁMICO ✨ ---
                        max_length=rx.cond(
                            AppState.price_str.length() > 0,
                            AppState.price_str.length(),
                            10 # Un límite por defecto si el precio está vacío
                        )
                        # --- ✨ FIN ✨ ---
                    )),
                    columns="2", spacing="4"
                ),
                rx.grid(
                    rx.vstack(rx.text("Incluye IVA (19%)"), rx.hstack(rx.switch(is_checked=AppState.price_includes_iva, on_change=AppState.set_price_includes_iva), rx.text(rx.cond(AppState.price_includes_iva, "Sí", "No")))),
                    rx.vstack(rx.text("Origen"), rx.hstack(rx.switch(is_checked=AppState.is_imported, on_change=AppState.set_is_imported), rx.text(rx.cond(AppState.is_imported, "Importado", "Nacional")))),
                    columns="2", spacing="4"
                ),
                rx.grid(
                    rx.vstack(rx.text("Costo de Envío Mínimo (Local)"), rx.input(value=AppState.shipping_cost_str, on_change=AppState.set_shipping_cost_str, placeholder="Ej: 3000"), rx.text("El costo final aumentará según la distancia.", size="1", color_scheme="gray"), align_items="stretch"),
                    rx.vstack(rx.text("Moda Completa"), rx.hstack(rx.switch(is_checked=AppState.is_moda_completa, on_change=AppState.set_is_moda_completa), rx.text(rx.cond(AppState.is_moda_completa, "Activo", "Inactivo"))), rx.input(value=AppState.free_shipping_threshold_str, on_change=AppState.set_free_shipping_threshold_str, is_disabled=~AppState.is_moda_completa), rx.text("Envío gratis en compras > $XXX.XXX", size="1", color_scheme="gray"), align_items="stretch"),
                    rx.vstack(rx.text("Envío Combinado"), rx.hstack(rx.switch(is_checked=AppState.combines_shipping, on_change=AppState.set_combines_shipping), rx.text(rx.cond(AppState.combines_shipping, "Activo", "Inactivo"))), rx.text("Permite que varios productos usen un solo envío.", size="1", color_scheme="gray"), align_items="stretch"),
                    rx.vstack(rx.text("Límite de Productos"), rx.input(value=AppState.shipping_combination_limit_str, on_change=AppState.set_shipping_combination_limit_str, is_disabled=~AppState.combines_shipping), rx.text("Máx. de items por envío.", size="1", color_scheme="gray"), align_items="stretch"),
                    columns="2", spacing="4"
                ),
                rx.vstack(
                    rx.text("Descripción", as_="div", size="3", weight="bold"),
                    rx.text_area(name="content", value=AppState.content, on_change=AppState.set_content, style={"height": "120px"}),
                    align_items="stretch", width="100%",
                ),
                spacing="4", align_items="stretch", width="100%",
            ),
            columns={"initial": "1", "lg": "500px 1fr"}, 
            spacing="6", 
            width="100%", 
            align_items="start",
        ),
        rx.hstack(
            rx.spacer(),
            rx.button(
                "Publicar Producto", 
                on_click=AppState.submit_and_publish_manual,
                color_scheme="violet", 
                size="3"
            ),
            width="100%", 
            margin_top="1em"
        ),
        spacing="5", 
        width="100%",
        max_width="1200px",
        # --- ✨ LÍNEA DUPLICADA ELIMINADA AQUÍ ✨ ---
    )

# --- Componente para la previsualización de la tarjeta ---
def post_preview(
    title: rx.Var[str],
    price_cop: rx.Var[str],
    first_image_url: rx.Var[str],
    is_imported: rx.Var[bool],
    shipping_cost_badge_text: rx.Var[str],
    is_moda_completa: rx.Var[bool],
    moda_completa_tooltip_text: rx.Var[str],
    combines_shipping: rx.Var[bool],
    envio_combinado_tooltip_text: rx.Var[str],
) -> rx.Component:
    def _preview_badge(text_content: rx.Var[str], color_scheme: str) -> rx.Component:
        light_colors = {"gray": {"bg": "#F1F3F5", "text": "#495057"}, "violet": {"bg": "#F3F0FF", "text": "#5F3DC4"}, "teal": {"bg": "#E6FCF5", "text": "#0B7285"}}
        dark_colors = {"gray": {"bg": "#373A40", "text": "#ADB5BD"}, "violet": {"bg": "#4D2C7B", "text": "#D0BFFF"}, "teal": {"bg": "#0C3D3F", "text": "#96F2D7"}}
        colors = rx.cond(AppState.card_theme_mode == "light", light_colors[color_scheme], dark_colors[color_scheme])
        
        return rx.box(
            rx.text(text_content, size="2", weight="medium"),
            bg=colors["bg"], 
            color=colors["text"],
            padding="1px 10px", 
            border_radius="var(--radius-full)", 
            font_size="0.8em",
            white_space="nowrap",
        )
    
    return rx.box(
        rx.vstack(
             rx.box(
                 rx.image(
                    src=rx.get_upload_url(first_image_url),
                    fallback="/image_off.png", 
                    width="100%", height="260px", object_fit="contain",
                    transform=rx.cond(
                        AppState.is_hydrated,
                         f"scale({AppState.preview_zoom}) rotate({AppState.preview_rotation}deg) translateX({AppState.preview_offset_x}px) translateY({AppState.preview_offset_y}px)",
                        "scale(1)"
                    ),
                    transition="transform 0.2s ease-out",
                ),
                rx.badge(
                     rx.cond(is_imported, "Importado", "Nacional"),
                    color_scheme=rx.cond(is_imported, "purple", "cyan"), variant="solid",
                    style={"position": "absolute", "top": "0.5rem", "left": "0.5rem", "z_index": "1"}
                ),
                position="relative", width="100%", height="260px",
                overflow="hidden", 
                border_top_left_radius="var(--radius-3)", border_top_right_radius="var(--radius-3)",
                bg=rx.cond(AppState.card_theme_mode == "light", "white", rx.color("gray", 3)),
             ),
             rx.vstack(
                # --- ✨ ESTA ES LA LÍNEA CORREGIDA ✨ ---
                rx.text(
                    rx.cond(title, title, "Título del Producto"),
                    weight="bold", size="6", width="100%",
                    # 1. Se ha restaurado la lógica de color completa:
                    color=rx.cond(
                        AppState.use_default_style, 
                        rx.color_mode_cond("var(--gray-11)", "white"), 
                        AppState.live_title_color
                    ),
                    # 2. Se ha añadido el estilo de 2 líneas:
                    style=TITLE_CLAMP_STYLE
                ),
                # --- ✨ FIN DE LA CORRECCIÓN ✨ ---
                star_rating_display_safe(0, 0, size=24),
                rx.text(
                    price_cop, size="5", weight="medium",
                    color=rx.cond(AppState.use_default_style, rx.color_mode_cond("var(--gray-9)", "var(--gray-a11)"), AppState.live_price_color)
                ),
                rx.spacer(),
                rx.vstack(
                    rx.grid(
                        _preview_badge(shipping_cost_badge_text, "gray"),
                        rx.cond(
                            is_moda_completa,
                            rx.tooltip(_preview_badge("Moda Completa", "violet"), content=moda_completa_tooltip_text),
                        ),
                        columns="auto auto",
                        spacing="2",
                        align="center",
                        justify="start",
                        width="100%",
                    ),
                    rx.cond(
                        combines_shipping,
                        rx.tooltip(_preview_badge("Envío Combinado", "teal"), content=envio_combinado_tooltip_text),
                    ),
                    spacing="1",
                    align_items="start",
                    width="100%",
                ),
                spacing="2", align_items="start", width="100%", padding="1em", flex_grow="1",
            ),
            spacing="0", align_items="stretch", height="100%",
        ),
        width="290px", height="480px",
        bg=rx.cond(AppState.use_default_style, rx.color_mode_cond("#fdfcff", "var(--gray-2)"), AppState.live_card_bg_color),
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
    
    first_image_url = rx.cond(
        (AppState.variant_groups.length() > 0) & (AppState.variant_groups[0].image_urls.length() > 0),
        AppState.variant_groups[0].image_urls[0],
        rx.cond(
            AppState.uploaded_images.length() > 0,
            AppState.uploaded_images[0],
            ""
        )
    )

    return rx.grid(
        rx.vstack(
            rx.heading("Crear Publicación", size="7", width="100%", text_align="left", margin_bottom="0.5em", color_scheme="gray", font_weight="medium"),
            blog_post_add_form(),
            width="100%", spacing="4", align_items="center",
            padding_left={"lg": "15em"}, padding_x=["1em", "2em"],
        ),
        rx.vstack(
            rx.heading("Previsualización", size="7", width="100%", text_align="left", margin_bottom="0.5em"),
            post_preview(
                title=AppState.title,
                price_cop=AppState.price_cop_preview,
                first_image_url=first_image_url,
                is_imported=AppState.is_imported,
                shipping_cost_badge_text=AppState.shipping_cost_badge_text_preview,
                is_moda_completa=AppState.is_moda_completa,
                moda_completa_tooltip_text=AppState.moda_completa_tooltip_text_preview,
                combines_shipping=AppState.combines_shipping,
                envio_combinado_tooltip_text=AppState.envio_combinado_tooltip_text_preview,
            ),
            image_editor_panel,
            # Se ha eliminado el 'display' responsivo para que sea visible en móvil
            width="100%", spacing="4", position="sticky", top="2em", align_items="center",
            on_mount=AppState.sync_preview_with_color_mode(rx.color_mode),
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