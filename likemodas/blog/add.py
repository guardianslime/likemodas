# En: likemodas/blog/add.py (VERSIÓN FINAL Y CORREGIDA)

import reflex as rx
from typing import Union # <-- Asegúrate de tener esta importación

# Importaciones de datos y modelos
from likemodas.data.product_options import (
    LISTA_TALLAS_ROPA, LISTA_NUMEROS_CALZADO, LISTA_TAMANOS_MOCHILAS
)
from ..state import (
    DEFAULT_DARK_BG, DEFAULT_DARK_PRICE, DEFAULT_DARK_TITLE,
    DEFAULT_LIGHT_BG, DEFAULT_LIGHT_PRICE, DEFAULT_LIGHT_TITLE,
    DEFAULT_LIGHT_IMAGE_BG, DEFAULT_DARK_IMAGE_BG,
    AppState, VariantGroupDTO, VariantFormData
)
from ..models import Category
from ..auth.admin_auth import require_panel_access
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


# --- Componente del formulario (CORREGIDO) ---
def blog_post_add_form() -> rx.Component:
    """
    [VERSIÓN CORREGIDA]
    Formulario completo para AÑADIR una nueva publicación, con la
    nueva lógica de gestión de grupos de imágenes y selección de imagen principal.
    """
    
    # --- ✨ INICIO: SECCIÓN DE IMÁGENES REEMPLAZADA (COPIADA DE EDITAR) ✨ ---
    def image_and_group_section() -> rx.Component:
        """
        [NUEVO] Sección para gestionar imágenes y grupos de color
        con el selector de imagen principal integrado (adaptado de 'editar').
        """
        
        # --- ✨ INICIO: MODIFICACIÓN PRINCIPAL DE ESTA FUNCIÓN ✨ ---
        unassigned_images_display = rx.vstack(
            rx.text("2. Selecciona imágenes para crear un nuevo grupo:", size="3", weight="medium"),
            rx.cond(
                AppState.unassigned_uploaded_images.length() == 0,
                rx.text("Todas las imágenes están en grupos o no hay imágenes subidas.", color_scheme="gray", size="2"),
                rx.flex(
                    rx.foreach(
                        AppState.unassigned_uploaded_images,
                        lambda img_name: rx.box(
                            rx.image(src=rx.get_upload_url(img_name), width="80px", height="80px", object_fit="cover", border_radius="md"),
                            rx.cond(
                                AppState.image_selection_for_grouping.contains(img_name),
                                rx.box(
                                    rx.text(AppState.selection_order_map[img_name], color="white", weight="bold", font_size="1.5em"),
                                    bg="rgba(90, 40, 180, 0.75)", position="absolute", inset="0", border_radius="md",
                                    display="flex", align_items="center", justify_content="center"
                                )
                            ),
                            rx.icon("x", on_click=lambda: AppState.remove_uploaded_image(img_name), style={"position": "absolute", "top": "-6px", "right": "-6px", "background": "var(--red-9)", "color": "white", "border_radius": "50%", "padding": "2px", "cursor": "pointer", "width": "18px", "height": "18px"}),
                            position="relative", border="2px solid",
                            border_color=rx.cond(AppState.image_selection_for_grouping.contains(img_name), "var(--violet-9)", "transparent"),
                            border_radius="lg", cursor="pointer",
                            on_click=lambda: AppState.toggle_image_selection_for_grouping(img_name),
                        )
                    ),
                    wrap="wrap", spacing="3", padding_top="0.5em",
                ),
            ),
            rx.button(
                "Crear Grupo de Color", 
                on_click=AppState.create_variant_group, 
                margin_top="0.5em", 
                width="100%", 
                type="button",
                is_disabled=AppState.image_selection_for_grouping.length() == 0 # Deshabilita si no hay selección
            ),
            spacing="3", width="100%", align_items="stretch",
        )
        
        integrated_group_and_image_selector = rx.vstack(
            rx.divider(margin_y="1em"),
            rx.text("3. Grupos y Selección de Imagen Principal", weight="bold", size="4"),
            rx.text("Haz clic en una imagen para seleccionarla como principal Y para editar los atributos de su grupo.", size="2", color_scheme="gray"),
            rx.scroll_area(
                rx.vstack(
                    rx.foreach(
                        AppState.variant_groups, # <-- Adaptado: usa variant_groups
                        lambda group_data, index: rx.vstack(
                            rx.text(f"Grupo {index + 1} ({group_data.attributes.get('Color', 'Sin Color')})", weight="medium", size="3"),
                            rx.flex(
                                rx.foreach(
                                    group_data.image_urls,
                                    lambda image_url: rx.box(
                                        rx.image(
                                            src=rx.get_upload_url(image_url),
                                            alt=f"Imagen {image_url}",
                                            width="70px",
                                            height="70px",
                                            object_fit="contain",
                                            bg="var(--gray-5)",
                                            # Borde si es la IMAGEN PRINCIPAL seleccionada
                                            border=rx.cond(
                                                AppState.live_preview_image_url == image_url, # <-- Adaptado: usa live_preview_image_url
                                                "3px solid var(--violet-9)",
                                                "1px solid var(--gray-7)"
                                            ),
                                            border_radius="md",
                                            cursor="pointer",
                                            
                                            # --- ✨ CORRECCIÓN 1 (IMAGEN) ✨ ---
                                            # Este clic AHORA SOLO selecciona la imagen principal
                                            on_click=[
                                                AppState.set_main_image_url_for_editing(image_url), # <-- Setea 'live_preview_image_url'
                                            ],
                                        ),
                                        padding="0.25em",
                                    ),
                                ),
                                wrap="wrap",
                                spacing="3",
                                width="100%",
                            ),
                            spacing="2",
                            align_items="start",
                            width="100%",
                            margin_bottom="0.5em",
                            
                            # Resaltado del GRUPO seleccionado para edición
                            border=rx.cond(AppState.selected_group_index == index, "2px solid var(--violet-7)", "1px solid var(--gray-5)"), # <-- Adaptado: usa selected_group_index
                            padding="0.75em",
                            border_radius="var(--radius-3)",
                            bg=rx.cond(AppState.selected_group_index == index, rx.color("violet", 2), "transparent"),
                            transition="background-color 0.2s, border-color 0.2s",

                            # --- ✨ CORRECCIÓN 2 (GRUPO) ✨ ---
                            # Este clic AHORA SOLO selecciona el grupo para edición
                            on_click=[
                                AppState.select_group_for_editing(index) # <-- Usa el setter de 'crear'
                            ],
                            cursor="pointer",
                        )
                    ),
                    spacing="3",
                    width="100%",
                ),
                type="auto",
                scrollbars="vertical",
                max_height="300px",
                width="100%",
                style={"border": "1px solid var(--gray-6)", "border_radius": "var(--radius-3)", "padding": "0.5em"}
            ),
            spacing="2",
            align_items="stretch",
            width="100%",
        )

        return rx.vstack(
            rx.text("1. Subir Imágenes (máx 10)", weight="bold"),
            rx.upload(
                 rx.vstack(rx.icon("upload"), rx.text("Añadir más imágenes")),
                 id="blog_upload", multiple=True, max_files=10, # <-- Adaptado: usa 'blog_upload'
                on_drop=AppState.handle_add_upload(rx.upload_files("blog_upload")), # <-- Adaptado: usa 'handle_add_upload'
                border="1px dashed var(--gray-a6)", padding="2em", width="100%"
            ),
            unassigned_images_display, # Aquí se inserta la nueva sección de imágenes no agrupadas
            
            rx.cond(
                AppState.variant_groups.length() > 0, 
                integrated_group_and_image_selector
            ),
            
            spacing="3", width="100%", align_items="stretch",
        )
    # --- ✨ FIN: SECCIÓN DE IMÁGENES REEMPLAZADA ✨ ---

    def attributes_and_stock_section() -> rx.Component:
        """
        Sección para atributos y stock del formulario de CREACIÓN.
        Define los atributos dinámicos (ropa, calzado, mochila) y corrige el layout del grid.
        """
        ropa_attributes = rx.vstack(
            rx.text("Talla"),
            rx.hstack(
                rx.select(LISTA_TALLAS_ROPA, placeholder="Añadir talla...", value=AppState.temp_talla, on_change=AppState.set_temp_talla),
                rx.button("Añadir", on_click=lambda: AppState.add_variant_attribute("Talla", AppState.temp_talla), type="button")
            ),
            rx.flex(
                 rx.foreach(AppState.attr_tallas_ropa, lambda talla: rx.badge(talla, rx.icon("x", size=12, on_click=lambda: AppState.remove_variant_attribute("Talla", talla), cursor="pointer"), variant="soft", color_scheme="gray")),
                wrap="wrap", spacing="2", min_height="28px", padding_top="0.5em"
            ),
            spacing="3", align_items="stretch", width="100%"
        )
        calzado_attributes = rx.vstack(
            rx.text("Número"),
            rx.hstack(
                rx.select(LISTA_NUMEROS_CALZADO, placeholder="Añadir número...", value=AppState.temp_numero, on_change=AppState.set_temp_numero),
                rx.button("Añadir", on_click=lambda: AppState.add_variant_attribute("Número", AppState.temp_numero), type="button")
            ),
            rx.flex(
                 rx.foreach(AppState.attr_numeros_calzado, lambda num: rx.badge(num, rx.icon("x", size=12, on_click=lambda: AppState.remove_variant_attribute("Número", num), cursor="pointer"), variant="soft", color_scheme="gray")),
                wrap="wrap", spacing="2", min_height="28px", padding_top="0.5em"
            ),
            spacing="3", align_items="stretch", width="100%"
        )
        mochilas_attributes = rx.vstack(
            rx.text("Tamaño"),
            rx.hstack(
                rx.select(LISTA_TAMANOS_MOCHILAS, placeholder="Añadir tamaño...", value=AppState.temp_tamano, on_change=AppState.set_temp_tamano),
                rx.button("Añadir", on_click=lambda: AppState.add_variant_attribute("Tamaño", AppState.temp_tamano), type="button")
            ),
            rx.flex(
                 rx.foreach(AppState.attr_tamanos_mochila, lambda tam: rx.badge(tam, rx.icon("x", size=12, on_click=lambda: AppState.remove_variant_attribute("Tamaño", tam), cursor="pointer"), variant="soft", color_scheme="gray")),
                wrap="wrap", spacing="2", min_height="28px", padding_top="0.5em"
            ),
            spacing="3", align_items="stretch", width="100%"
        )

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
                        rx.cond(
                            AppState.category == Category.ROPA.value, ropa_attributes,
                            rx.cond(AppState.category == Category.CALZADO.value, calzado_attributes,
                                rx.cond(AppState.category == Category.MOCHILAS.value, mochilas_attributes,
                                    rx.text("Selecciona categoría.", color_scheme="gray")
                                )
                            )
                        ),
                        rx.button("Guardar Atributos", on_click=AppState.update_group_attributes, margin_top="1em", size="2", variant="outline", type="button"),
                        rx.divider(margin_y="1em"),
                        rx.text("Fondo Lightbox (Sitio Claro)", weight="medium"),
                        rx.segmented_control.root(
                            rx.segmented_control.item("Oscuro", value="dark"),
                            rx.segmented_control.item("Blanco", value="white"),
                            value=AppState.temp_lightbox_bg_light,
                            on_change=AppState.set_temp_lightbox_bg_light,
                            color_scheme="gray", size="1",
                        ),
                        rx.text("Fondo Lightbox (Sitio Oscuro)", weight="medium", margin_top="0.5em"),
                        rx.segmented_control.root(
                            rx.segmented_control.item("Oscuro", value="dark"),
                            rx.segmented_control.item("Blanco", value="white"),
                            value=AppState.temp_lightbox_bg_dark,
                            on_change=AppState.set_temp_lightbox_bg_dark,
                            color_scheme="gray", size="1",
                        ),
                        spacing="3", align_items="stretch",
                    ), 
                    rx.vstack(
                        rx.text("Variantes y Stock", weight="medium"),
                        rx.button("Generar / Actualizar Variantes", on_click=lambda: AppState.generate_variants_for_group(AppState.selected_group_index), type="button"),
                        rx.cond(
                            AppState.generated_variants_map.contains(AppState.selected_group_index),
                            rx.scroll_area(
                                rx.vstack(
                                    rx.foreach(
                                        AppState.generated_variants_map[AppState.selected_group_index],
                                        lambda variant, var_index: rx.hstack(
                                            rx.text(variant.attributes.get("Talla", variant.attributes.get("Número", variant.attributes.get("Tamaño", "N/A")))),
                                            rx.spacer(),
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

    # --- Estructura principal del formulario de CREACIÓN (sin cambios) ---
    return rx.form(
        rx.vstack(
            rx.grid(
                # Columna izquierda (Imágenes y Variantes)
                rx.vstack(
                    image_and_group_section(), 
                    attributes_and_stock_section(),
                    spacing="5", width="100%",
                ),
                # Columna derecha (Detalles del Producto)
                rx.vstack(
                    rx.vstack(
                        rx.text("Título del Producto"),
                        rx.input(name="title", value=AppState.title, on_change=AppState.set_title, required=True, max_length=40),
                        align_items="stretch"
                    ),
                    rx.grid(
                        rx.vstack(rx.text("Categoría"), rx.select(AppState.categories, name="category", required=True, value=AppState.category, on_change=AppState.set_category), align_items="stretch"),
                        rx.vstack(rx.text("Tipo"), searchable_select(placeholder="Selecciona un Tipo", options=AppState.filtered_attr_tipos, value_select=AppState.attr_tipo, on_change_select=AppState.set_attr_tipo, search_value=AppState.search_attr_tipo, on_change_search=AppState.set_search_attr_tipo, filter_name="add_tipo_filter", is_disabled=~AppState.category), align_items="stretch"),
                        rx.vstack(
                            rx.text(AppState.material_label),
                            searchable_select(placeholder=rx.cond(AppState.category, f"Selecciona {AppState.material_label}", "Elige categoría primero"), options=AppState.filtered_attr_materiales, value_select=AppState.attr_material, on_change_select=AppState.set_attr_material, search_value=AppState.search_attr_material, on_change_search=AppState.set_search_attr_material, filter_name="add_material_filter", is_disabled=~AppState.category)
                        , align_items="stretch"),
                        columns={"initial": "1", "md": "3"}, spacing="4", width="100%"
                    ),
                    rx.grid(
                        rx.vstack(rx.text("Precio (COP)"), rx.input(name="price", value=AppState.price_str, on_change=AppState.set_price_str, on_blur=AppState.validate_price_on_blur_add, type="number", required=True, placeholder="Ej: 55000"), align_items="stretch"),
                        rx.vstack(rx.text("Ganancia (COP)"), rx.input(name="profit", value=AppState.profit_str, on_change=AppState.set_profit_str, on_blur=AppState.validate_profit_on_blur_add, type="number", placeholder="Ej: 15000"), align_items="stretch"),
                        columns="2", spacing="4", width="100%"
                    ),
                    rx.grid(
                        rx.vstack(rx.text("Incluye IVA (19%)"), rx.hstack(rx.switch(name="price_includes_iva", is_checked=AppState.price_includes_iva, on_change=AppState.set_price_includes_iva), rx.text(rx.cond(AppState.price_includes_iva, "Sí", "No")))),
                        rx.vstack(rx.text("Origen"), rx.hstack(rx.switch(name="is_imported", is_checked=AppState.is_imported, on_change=AppState.set_is_imported), rx.text(rx.cond(AppState.is_imported, "Importado", "Nacional")))),
                        columns="2", spacing="4", width="100%"
                    ),
                    rx.grid(
                        rx.vstack(rx.text("Costo de Envío Mínimo (Local)"), rx.input(name="shipping_cost_str", value=AppState.shipping_cost_str, on_change=AppState.set_shipping_cost_str, placeholder="Ej: 3000"), rx.text("El costo final aumentará según la distancia.", size="1", color_scheme="gray"), align_items="stretch"),
                        rx.vstack(rx.text("Moda Completa"), rx.hstack(rx.switch(name="is_moda_completa", is_checked=AppState.is_moda_completa, on_change=AppState.set_is_moda_completa), rx.text(rx.cond(AppState.is_moda_completa, "Activo", "Inactivo"))), rx.input(name="free_shipping_threshold_str", value=AppState.free_shipping_threshold_str, on_change=AppState.set_free_shipping_threshold_str, is_disabled=~AppState.is_moda_completa, placeholder="Monto para envío gratis"), rx.text("Envío gratis en compras > este monto.", size="1", color_scheme="gray"), align_items="stretch"),
                        rx.vstack(rx.text("Envío Combinado"), rx.hstack(rx.switch(name="combines_shipping", is_checked=AppState.combines_shipping, on_change=AppState.set_combines_shipping), rx.text(rx.cond(AppState.combines_shipping, "Activo", "Inactivo"))), rx.text("Permite que varios productos usen un solo envío.", size="1", color_scheme="gray"), align_items="stretch"),
                        rx.vstack(rx.text("Límite de Productos"), rx.input(name="shipping_combination_limit_str", value=AppState.shipping_combination_limit_str, on_change=AppState.set_shipping_combination_limit_str, is_disabled=~AppState.combines_shipping, placeholder="Máx. de items por envío"), rx.text("Máx. de items por envío combinado.", size="1", color_scheme="gray"), align_items="stretch"),
                        columns="2", spacing="4", width="100%"
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
                rx.button("Publicar Producto", type="submit", size="3", margin_top="2em"), 
                width="100%",
            ),
            spacing="5",
            width="100%",
        ),
        on_submit=AppState.submit_and_publish_manual,
        reset_on_submit=False,
        width="100%"
    )


# --- Componente para la previsualización de la tarjeta (CORREGIDO) ---
def post_preview(
    title: rx.Var[str],
    price_cop: rx.Var[str],
    is_imported: rx.Var[bool],
    shipping_cost_badge_text: rx.Var[str],
    is_moda_completa: rx.Var[bool],
    moda_completa_tooltip_text: rx.Var[str],
    combines_shipping: rx.Var[bool],
    envio_combinado_tooltip_text: rx.Var[str],
) -> rx.Component:
    """
    [VERSIÓN FINAL CON HEX Y SELECCIÓN DE IMAGEN PRINCIPAL]
    Muestra la previsualización de la tarjeta de producto, asegurando que TODOS
    sus elementos (fondo imagen, badges) respeten la apariencia seleccionada
    y la imagen principal seleccionada.
    """
    is_light_preview = AppState.card_theme_mode == "light"

    card_target_appearance = rx.cond(
        AppState.is_in_edit_preview,
        rx.cond(
            is_light_preview,
            AppState.edit_light_mode_appearance,
            AppState.edit_dark_mode_appearance
        ),
        rx.cond(
            is_light_preview,
            AppState.light_mode_appearance,
            AppState.dark_mode_appearance
        )
    )

    def _preview_badge(text_content: rx.Var[str], color_scheme: str) -> rx.Component:
        light_colors = {"gray": {"bg": "#F1F3F5", "text": "#495057"}, "violet": {"bg": "#F3F0FF", "text": "#5F3DC4"}, "teal": {"bg": "#E6FCF5", "text": "#0B7285"}}
        dark_colors = {"gray": {"bg": "#373A40", "text": "#ADB5BD"}, "violet": {"bg": "#4D2C7B", "text": "#D0BFFF"}, "teal": {"bg": "#0C3D3F", "text": "#96F2D7"}}
        
        colors = rx.cond(card_target_appearance == "light", light_colors[color_scheme], dark_colors[color_scheme])
        
        return rx.box(
            rx.text(text_content, size="2", weight="medium"),
            bg=colors["bg"], color=colors["text"], padding="1px 10px",
            border_radius="var(--radius-full)", font_size="0.8em", white_space="nowrap",
        )

    card_bg_color = AppState.live_card_bg_color
    title_color = AppState.live_title_color
    price_color = AppState.live_price_color

    # --- ✨ INICIO: CORRECCIÓN DEL FONDO DE IMAGEN ✨ ---
    # Usar las nuevas constantes que definimos en state.py
    image_bg = rx.cond(
        card_target_appearance == "light",
        DEFAULT_LIGHT_IMAGE_BG,
        DEFAULT_DARK_IMAGE_BG
    )
    # --- ✨ FIN: CORRECCIÓN DEL FONDO DE IMAGEN ✨ ---

    return rx.box(
         rx.vstack(
             rx.box( # Contenedor de la imagen
                rx.cond(
                    AppState.live_preview_image_url != "",
                    rx.image(
                        src=rx.get_upload_url(AppState.live_preview_image_url), 
                        alt="Previsualización del Producto",
                        width="280px",
                        height="280px",
                        object_fit="contain",
                        transform=rx.cond(
                            AppState.is_hydrated,
                            f"scale({AppState.preview_zoom}) rotate({AppState.preview_rotation}deg) translateX({AppState.preview_offset_x}px) translateY({AppState.preview_offset_y}px)",
                            "scale(1)"
                        ),
                        transition="transform 0.2s ease-out",
                    ),
                    rx.box(
                        rx.vstack(
                            rx.icon("image-off", size=48, color_scheme="gray"),
                            rx.text("Sube una imagen y crea un grupo", size="2", color_scheme="gray", max_width="150px", text_align="center"),
                            spacing="3",
                            align="center"
                        ),
                        width="100%", 
                        height="260px", 
                        display="flex", 
                        align_items="center", 
                        justify_content="center"
                    )
                ),
                 rx.badge( 
                    rx.cond(is_imported, "Importado", "Nacional"),
                    color_scheme=rx.cond(is_imported, "purple", "cyan"), variant="solid",
                    style={"position": "absolute", "top": "0.5rem", "left": "0.5rem", "z_index": "1"}
                 ),
                 position="relative", width="100%", height="260px",
                 overflow="hidden",
                 border_top_left_radius="var(--radius-3)", border_top_right_radius="var(--radius-3)",
                 bg=image_bg,
             ),
             rx.vstack( # Contenedor de la información
                rx.text( 
                    rx.cond(title, title, "Título del Producto"),
                    weight="bold", size="6", width="100%",
                    color=title_color, 
                    style=TITLE_CLAMP_STYLE
                ),
                star_rating_display_safe(0, 0, size=24), 
                rx.text( 
                    price_cop, size="5", weight="medium",
                    color=price_color
                 ),
                rx.spacer(),
                rx.vstack( 
                    rx.grid(
                        _preview_badge(shipping_cost_badge_text, "gray"),
                        rx.cond(
                             is_moda_completa,
                            rx.tooltip(_preview_badge("Moda Completa", "violet"), content=moda_completa_tooltip_text),
                        ),
                        columns="auto auto", spacing="2", align="center", justify="start", width="100%",
                    ),
                     rx.cond(
                        combines_shipping,
                        rx.tooltip(_preview_badge("Envío Combinado", "teal"), content=envio_combinado_tooltip_text),
                    ),
                    spacing="1", align_items="start", width="100%",
                ),
                spacing="2", align_items="start", width="100%", padding="1em", flex_grow="1",
             ),
            spacing="0", align_items="stretch", height="100%",
        ),
        width="290px", height="480px",
        bg=card_bg_color, 
        border="1px solid var(--gray-a6)",
        border_radius="8px", box_shadow="md",
    )

# --- Contenido de la Página (Layout) ---
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
    
    personalizar_tarjeta_panel = rx.vstack(
        rx.divider(margin_y="1em"),
        rx.hstack(
            rx.text("Personalizar Tarjeta", weight="bold", size="4"),
            rx.spacer(),
            rx.tooltip(
                rx.icon_button(
                    rx.icon("rotate-ccw", size=14),
                    on_click=AppState.reset_card_styles_to_default,
                    variant="ghost", color_scheme="gray", size="1", type="button",
                ),
                content="Restablecer estilos"
            ),
            justify="between", width="100%", align="center",
        ),
        rx.hstack(
            rx.text("Usar estilo predeterminado", size="3"),
            rx.spacer(),
            rx.switch(is_checked=AppState.use_default_style, on_change=AppState.set_use_default_style, size="2"),
            width="100%", align="center",
        ),
        rx.cond(
            AppState.use_default_style,
            rx.vstack(
                rx.divider(margin_top="1em"),
                rx.text("Apariencia en Modo Claro:", size="3"),
                rx.segmented_control.root(
                    rx.segmented_control.item("Claro", value="light"),
                    rx.segmented_control.item("Oscuro", value="dark"),
                    value=AppState.light_mode_appearance, 
                    on_change=AppState.set_light_mode_appearance, 
                    width="100%", color_scheme="violet",
                ),
                rx.divider(margin_top="1em"),
                rx.text("Apariencia en Modo Oscuro:", size="3"),
                rx.segmented_control.root(
                    rx.segmented_control.item("Claro", value="light"),
                    rx.segmented_control.item("Oscuro", value="dark"),
                    value=AppState.dark_mode_appearance, 
                    on_change=AppState.set_dark_mode_appearance, 
                    width="100%", color_scheme="violet",
                ),
                spacing="3", width="100%", margin_top="1em"
            ),
        ),
        rx.divider(margin_top="1em"),
        rx.text("Previsualizar como:", size="2", weight="medium", margin_top="0.5em"),
        rx.segmented_control.root(
            rx.segmented_control.item("Modo Claro", value="light"),
            rx.segmented_control.item("Modo Oscuro", value="dark"),
            on_change=AppState.toggle_preview_mode,
            value=AppState.card_theme_mode,
            width="100%",
        ),
        spacing="3", padding="1em", border="1px dashed var(--gray-a6)",
        border_radius="md", margin_top="1.5em", align_items="stretch",
        width="290px",
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
                is_imported=AppState.is_imported,
                shipping_cost_badge_text=AppState.shipping_cost_badge_text_preview,
                is_moda_completa=AppState.is_moda_completa,
                moda_completa_tooltip_text=AppState.moda_completa_tooltip_text_preview,
                combines_shipping=AppState.combines_shipping,
                envio_combinado_tooltip_text=AppState.envio_combinado_tooltip_text_preview,
            ),
            
            image_editor_panel, 
            
            personalizar_tarjeta_panel,

            width="100%", spacing="4", position="sticky", top="2em", align_items="center",
            
            # --- ✨ INICIO: CORRECCIÓN DE PREVISUALIZACIÓN (Añadir on_mount) ✨ ---
            on_mount=[
                AppState.set_preview_context_to_add, # <-- Pone el flag en modo "Crear"
                AppState.sync_preview_with_color_mode(rx.color_mode) # Sincroniza el tema
            ],
            # --- ✨ FIN: CORRECCIÓN DE PREVISUALIZACIÓN ✨ ---
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