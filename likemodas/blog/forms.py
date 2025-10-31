# En: likemodas/blog/forms.py (VERSIÓN COMPLETA Y CORREGIDA)

import reflex as rx
from ..state import AppState, VariantGroupDTO, VariantFormData
from ..models import Category
from ..ui.components import searchable_select
from ..data.product_options import (
    LISTA_COLORES, LISTA_NUMEROS_CALZADO, LISTA_TALLAS_ROPA, LISTA_TAMANOS_MOCHILAS,
    MATERIALES_ROPA, MATERIALES_CALZADO, MATERIALES_MOCHILAS, LISTA_MATERIALES
)

# =============================================================================
# FORMULARIO PARA CREAR PUBLICACIONES (COMPLETO)
# =============================================================================
def blog_post_add_form() -> rx.Component:
    """
    Formulario para AÑADIR una nueva publicación.
    """
    # --- Componentes internos de la UI ---
    def image_and_group_section() -> rx.Component:
        """Sección para subir imágenes y crear grupos de color."""
        def render_group_card(group: VariantGroupDTO, index: rx.Var[int]) -> rx.Component:
            """Renderiza una tarjeta para un grupo de variantes existente."""
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
                    on_click=lambda: AppState.remove_variant_group(index), # Usar lambda
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
                on_click=lambda: AppState.select_group_for_editing(index), # Usar lambda
            )

        return rx.vstack(
            rx.text("1. Subir Imágenes (máx 10)", weight="bold"),
            rx.upload(
                 rx.vstack(rx.icon("upload"), rx.text("Arrastra o haz clic")),
                id="blog_upload", multiple=True, max_files=10,
                on_drop=AppState.handle_add_upload(rx.upload_files("blog_upload")),
                border="1px dashed var(--gray-a6)", padding="2em", width="100%"
            ),
            rx.text("2. Selecciona imágenes para crear un grupo de color:"),
            rx.flex(
                 rx.foreach(
                    AppState.uploaded_images,
                    lambda img_name: rx.box(
                        rx.image(src=rx.get_upload_url(img_name), width="80px", height="80px", object_fit="cover", border_radius="md"),
                        rx.cond(
                            AppState.image_selection_for_grouping.contains(img_name), # Usa .contains()
                            rx.box(
                                rx.text(AppState.selection_order_map[img_name], color="white", weight="bold", font_size="1.5em"),
                                bg="rgba(90, 40, 180, 0.75)", position="absolute", inset="0", border_radius="md",
                                display="flex", align_items="center", justify_content="center"
                            )
                        ),
                        rx.icon("x", on_click=lambda: AppState.remove_uploaded_image(img_name), style={"position": "absolute", "top": "-6px", "right": "-6px", "background": "var(--red-9)", "color": "white", "border_radius": "50%", "padding": "2px", "cursor": "pointer", "width": "18px", "height": "18px"}),
                        position="relative", border="2px solid",
                        border_color=rx.cond(AppState.image_selection_for_grouping.contains(img_name), "var(--violet-9)", "transparent"), # Usa .contains()
                        border_radius="lg", cursor="pointer",
                        on_click=lambda: AppState.toggle_image_selection_for_grouping(img_name),
                    )
                ),
                 wrap="wrap", spacing="3", padding_top="0.5em",
             ),
            rx.button("Crear Grupo de Color", on_click=AppState.create_variant_group, margin_top="0.5em", width="100%", type="button"),
            rx.divider(margin_y="1em"),
            rx.text("3. Grupos existentes (Selecciona uno para editar abajo):"),
            rx.flex(rx.foreach(AppState.variant_groups, render_group_card), wrap="wrap", spacing="2"),
            spacing="3", width="100%", align_items="stretch",
        )

    def attributes_and_stock_section() -> rx.Component:
        """Sección para definir atributos (color, talla, etc.) y stock del grupo seleccionado."""
        # --- Define los componentes de atributos dinámicos ---
        ropa_attributes = rx.vstack(
            rx.text("Talla"),
            rx.hstack(
                rx.select(LISTA_TALLAS_ROPA, placeholder="Añadir talla...", value=AppState.temp_talla, on_change=AppState.set_temp_talla),
                rx.button("Añadir", on_click=lambda: AppState.add_variant_attribute("Talla", AppState.temp_talla), type="button") # Usar lambda
            ),
            rx.flex(
                 rx.foreach(AppState.attr_tallas_ropa, lambda talla: rx.badge(talla, rx.icon("x", size=12, on_click=lambda: AppState.remove_variant_attribute("Talla", talla), cursor="pointer"), variant="soft", color_scheme="gray")), # Usar lambda
                wrap="wrap", spacing="2", min_height="28px", padding_top="0.5em"
            ),
            spacing="3", align_items="stretch", width="100%"
        )
        calzado_attributes = rx.vstack(
            rx.text("Número"),
            rx.hstack(
                rx.select(LISTA_NUMEROS_CALZADO, placeholder="Añadir número...", value=AppState.temp_numero, on_change=AppState.set_temp_numero),
                rx.button("Añadir", on_click=lambda: AppState.add_variant_attribute("Número", AppState.temp_numero), type="button") # Usar lambda
            ),
            rx.flex(
                 rx.foreach(AppState.attr_numeros_calzado, lambda num: rx.badge(num, rx.icon("x", size=12, on_click=lambda: AppState.remove_variant_attribute("Número", num), cursor="pointer"), variant="soft", color_scheme="gray")), # Usar lambda
                wrap="wrap", spacing="2", min_height="28px", padding_top="0.5em"
            ),
            spacing="3", align_items="stretch", width="100%"
        )
        mochilas_attributes = rx.vstack(
            rx.text("Tamaño"),
            rx.hstack(
                rx.select(LISTA_TAMANOS_MOCHILAS, placeholder="Añadir tamaño...", value=AppState.temp_tamano, on_change=AppState.set_temp_tamano),
                rx.button("Añadir", on_click=lambda: AppState.add_variant_attribute("Tamaño", AppState.temp_tamano), type="button") # Usar lambda
            ),
            rx.flex(
                 rx.foreach(AppState.attr_tamanos_mochila, lambda tam: rx.badge(tam, rx.icon("x", size=12, on_click=lambda: AppState.remove_variant_attribute("Tamaño", tam), cursor="pointer"), variant="soft", color_scheme="gray")), # Usar lambda
                wrap="wrap", spacing="2", min_height="28px", padding_top="0.5em"
            ),
            spacing="3", align_items="stretch", width="100%"
        )
        # --- Fin componentes dinámicos ---

        return rx.cond(
             AppState.selected_group_index >= 0,
            rx.vstack(
                 rx.divider(margin_y="1.5em"),
                rx.heading(f"4. Atributos y Stock Grupo #{AppState.selected_group_index + 1}", size="5"),
                rx.grid(
                    # --- Columna 1: Atributos y Fondos Lightbox ---
                    rx.vstack(
                        rx.text("Atributos del Grupo", weight="medium"),
                        rx.text("Color"),
                        searchable_select( # Selector de color
                            placeholder="Seleccionar color...", options=AppState.filtered_attr_colores,
                            on_change_select=AppState.set_temp_color, value_select=AppState.temp_color,
                            search_value=AppState.search_attr_color, on_change_search=AppState.set_search_attr_color,
                            filter_name="color_filter_main",
                        ),
                        # Renderizado condicional de Talla/Número/Tamaño
                        rx.cond(
                            AppState.category == Category.ROPA.value, ropa_attributes,
                            rx.cond(AppState.category == Category.CALZADO.value, calzado_attributes,
                                rx.cond(AppState.category == Category.MOCHILAS.value, mochilas_attributes,
                                    rx.text("Selecciona categoría.", color_scheme="gray")
                                )
                            )
                        ),
                        rx.button("Guardar Atributos", on_click=AppState.update_group_attributes, margin_top="1em", size="2", variant="outline", type="button"),

                        # --- Campos de Lightbox ---
                        rx.divider(margin_y="1em"),
                        rx.text("Fondo Lightbox (Sitio Claro)", weight="medium"),
                        rx.segmented_control.root(
                            rx.segmented_control.item("Oscuro", value="dark"),
                            rx.segmented_control.item("Blanco", value="white"),
                            value=AppState.temp_lightbox_bg_light, # Usa 'temp_' para CREAR
                            on_change=AppState.set_temp_lightbox_bg_light,
                            color_scheme="gray", size="1",
                        ),
                        rx.text("Fondo Lightbox (Sitio Oscuro)", weight="medium", margin_top="0.5em"),
                        rx.segmented_control.root(
                            rx.segmented_control.item("Oscuro", value="dark"),
                            rx.segmented_control.item("Blanco", value="white"),
                            value=AppState.temp_lightbox_bg_dark, # Usa 'temp_' para CREAR
                            on_change=AppState.set_temp_lightbox_bg_dark,
                            color_scheme="gray", size="1",
                        ),
                        spacing="3", align_items="stretch",
                    ), # Fin vstack columna 1

                    # --- Columna 2: Variantes y Stock ---
                    rx.vstack(
                        rx.text("Variantes y Stock", weight="medium"),
                        rx.button("Generar / Actualizar Variantes", on_click=lambda: AppState.generate_variants_for_group(AppState.selected_group_index), type="button"), # Usar lambda
                        rx.cond(
                            AppState.generated_variants_map.contains(AppState.selected_group_index),
                            rx.scroll_area(
                                rx.vstack(
                                    rx.foreach(
                                        AppState.generated_variants_map[AppState.selected_group_index],
                                        lambda variant, var_index: rx.hstack(
                                            # Muestra atributo dinámico
                                            rx.text(variant.attributes.get("Talla", variant.attributes.get("Número", variant.attributes.get("Tamaño", "N/A")))),
                                            rx.spacer(),
                                            # Botones +/- y Input de stock
                                            rx.icon_button(rx.icon("minus"), on_click=lambda: AppState.decrement_variant_stock(AppState.selected_group_index, var_index), size="1", type="button"), # Usar lambda
                                            rx.input(value=variant.stock.to_string(), on_change=lambda val: AppState.set_variant_stock(AppState.selected_group_index, var_index, val), text_align="center", max_width="50px"), # Usar lambda
                                            rx.icon_button(rx.icon("plus"), on_click=lambda: AppState.increment_variant_stock(AppState.selected_group_index, var_index), size="1", type="button"), # Usar lambda
                                            align="center"
                                         )
                                    ),
                                    spacing="2", width="100%", padding_top="1em"
                                 ),
                                max_height="200px", type="auto", scrollbars="vertical"
                            )
                        ),
                        spacing="3", align_items="stretch",
                    ), # Fin vstack columna 2
                    columns="2", spacing="4", width="100%" # Estilos del grid
                ),
                align_items="stretch", width="100%" # Estilos vstack principal
            ) # Fin vstack principal
        ) # Fin rx.cond

    # --- Estructura principal del formulario de CREACIÓN ---
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
                    # Sección Categoría, Tipo, Material/Tela
                    rx.grid(
                        rx.vstack(rx.text("Categoría"), rx.select(AppState.categories, name="category", required=True, value=AppState.category, on_change=AppState.set_category), align_items="stretch"),
                        rx.vstack(rx.text("Tipo"), searchable_select(placeholder="Selecciona un Tipo", options=AppState.filtered_attr_tipos, value_select=AppState.attr_tipo, on_change_select=AppState.set_attr_tipo, search_value=AppState.search_attr_tipo, on_change_search=AppState.set_search_attr_tipo, filter_name="add_tipo_filter", is_disabled=~AppState.category), align_items="stretch"),
                        rx.vstack(
                            rx.text(AppState.material_label),
                            searchable_select(placeholder=rx.cond(AppState.category, f"Selecciona {AppState.material_label}", "Elige categoría primero"), options=AppState.filtered_attr_materiales, value_select=AppState.attr_material, on_change_select=AppState.set_attr_material, search_value=AppState.search_attr_material, on_change_search=AppState.set_search_attr_material, filter_name="add_material_filter", is_disabled=~AppState.category)
                        , align_items="stretch"),
                        columns={"initial": "1", "md": "3"}, spacing="4", width="100%"
                    ),
                    # Sección Precio, Ganancia
                    rx.grid(
                        rx.vstack(rx.text("Precio (COP)"), rx.input(name="price", value=AppState.price_str, on_change=AppState.set_price_str, on_blur=AppState.validate_price_on_blur_add, type="number", required=True, placeholder="Ej: 55000"), align_items="stretch"),
                        rx.vstack(rx.text("Ganancia (COP)"), rx.input(name="profit", value=AppState.profit_str, on_change=AppState.set_profit_str, on_blur=AppState.validate_profit_on_blur_add, type="number", placeholder="Ej: 15000"), align_items="stretch"),
                        columns="2", spacing="4", width="100%"
                    ),
                    # Sección IVA, Origen
                    rx.grid(
                        rx.vstack(rx.text("Incluye IVA (19%)"), rx.hstack(rx.switch(name="price_includes_iva", is_checked=AppState.price_includes_iva, on_change=AppState.set_price_includes_iva), rx.text(rx.cond(AppState.price_includes_iva, "Sí", "No")))),
                        rx.vstack(rx.text("Origen"), rx.hstack(rx.switch(name="is_imported", is_checked=AppState.is_imported, on_change=AppState.set_is_imported), rx.text(rx.cond(AppState.is_imported, "Importado", "Nacional")))),
                        columns="2", spacing="4", width="100%"
                    ),
                    # Sección Envío
                    rx.grid(
                        rx.vstack(rx.text("Costo de Envío Mínimo (Local)"), rx.input(name="shipping_cost_str", value=AppState.shipping_cost_str, on_change=AppState.set_shipping_cost_str, placeholder="Ej: 3000"), rx.text("El costo final aumentará según la distancia.", size="1", color_scheme="gray"), align_items="stretch"),
                        rx.vstack(rx.text("Moda Completa"), rx.hstack(rx.switch(name="is_moda_completa", is_checked=AppState.is_moda_completa, on_change=AppState.set_is_moda_completa), rx.text(rx.cond(AppState.is_moda_completa, "Activo", "Inactivo"))), rx.input(name="free_shipping_threshold_str", value=AppState.free_shipping_threshold_str, on_change=AppState.set_free_shipping_threshold_str, is_disabled=~AppState.is_moda_completa, placeholder="Monto para envío gratis"), rx.text("Envío gratis en compras > este monto.", size="1", color_scheme="gray"), align_items="stretch"),
                        rx.vstack(rx.text("Envío Combinado"), rx.hstack(rx.switch(name="combines_shipping", is_checked=AppState.combines_shipping, on_change=AppState.set_combines_shipping), rx.text(rx.cond(AppState.combines_shipping, "Activo", "Inactivo"))), rx.text("Permite que varios productos usen un solo envío.", size="1", color_scheme="gray"), align_items="stretch"),
                        rx.vstack(rx.text("Límite de Productos"), rx.input(name="shipping_combination_limit_str", value=AppState.shipping_combination_limit_str, on_change=AppState.set_shipping_combination_limit_str, is_disabled=~AppState.combines_shipping, placeholder="Máx. de items por envío"), rx.text("Máx. de items por envío combinado.", size="1", color_scheme="gray"), align_items="stretch"),
                        columns="2", spacing="4", width="100%"
                    ),
                    # Sección Descripción
                    rx.vstack(
                        rx.text("Descripción", as_="div", size="3", weight="bold"),
                        rx.text_area(name="content", value=AppState.content, on_change=AppState.set_content, style={"height": "120px"}),
                        align_items="stretch", width="100%",
                    ),
                    spacing="4", align_items="stretch", width="100%",
                ),
                columns={"initial": "1", "lg": "500px 1fr"}, spacing="6", width="100%", align_items="start",
            ),
            # Botón de Publicar
            rx.hstack(
                rx.spacer(),
                rx.button("Publicar Producto", type="submit", size="3", margin_top="2em"), # type="submit" para que el form lo maneje
                width="100%",
            ),
            spacing="5", width="100%", # Estilos vstack principal
        ), # Fin vstack principal
        # on_submit y reset_on_submit APLICADOS AL rx.form
        on_submit=AppState.submit_and_publish_manual, # Evento correcto
        reset_on_submit=False, # Evita reseteos inesperados
        width="100%"
    ) # Fin del rx.form

# =============================================================================
# FORMULARIO DE EDICIÓN (COMPLETAMENTE RECONSTRUIDO Y CORREGIDO)
# =============================================================================
# --- ✨ INICIO: LA FIRMA DE LA FUNCIÓN AHORA ACEPTA EL ARGUMENTO ✨ ---
def blog_post_edit_form(main_image_selector: rx.Component) -> rx.Component:
# --- ✨ FIN ✨ ---
    """
    [VERSIÓN FINAL Y CORREGIDA] Formulario para EDITAR una publicación.
    Ahora acepta el selector de imagen principal como argumento.
    """
    def image_and_group_section() -> rx.Component:
        """Sección para gestionar imágenes y grupos de color en EDICIÓN."""
        def render_group_card(group: VariantGroupDTO, index: rx.Var[int]) -> rx.Component:
            """Renderiza una tarjeta para un grupo de variantes existente en EDICIÓN."""
            is_selected = AppState.edit_selected_group_index == index
            return rx.box(
                rx.flex(
                    rx.foreach(group.image_urls, lambda url: rx.image(src=rx.get_upload_url(url), width="40px", height="40px", object_fit="cover", border_radius="sm")),
                    wrap="wrap", spacing="2",
                ),
                rx.icon("trash-2", on_click=AppState.remove_edit_variant_group(index), style={"position": "absolute", "top": "-8px", "right": "-8px", "background": "var(--red-9)", "color": "white", "border_radius": "50%", "padding": "2px", "cursor": "pointer", "width": "20px", "height": "20px"}),
                position="relative", border_width="2px",
                border_color=rx.cond(is_selected, "var(--violet-9)", "transparent"),
                padding="0.25em", border_radius="md", cursor="pointer",
                on_click=AppState.select_edit_group_for_editing(index),
            )

        return rx.vstack(
            rx.text("1. Imágenes del Producto", weight="bold"),
            rx.upload(
                 rx.vstack(rx.icon("upload"), rx.text("Añadir más imágenes")),
                id="edit_upload", multiple=True, max_files=10,
                on_drop=AppState.handle_edit_upload(rx.upload_files("edit_upload")),
                border="1px dashed var(--gray-a6)", padding="2em", width="100%"
            ),
            rx.text("2. Selecciona y ordena las imágenes para crear/editar un grupo:"),
            rx.flex(
                 rx.foreach(
                    AppState.edit_uploaded_images,
                    lambda img_name: rx.box(
                        rx.image(src=rx.get_upload_url(img_name), width="80px", height="80px", object_fit="cover", border_radius="md"),
                        rx.cond(
                            AppState.edit_image_selection_for_grouping.contains(img_name),
                            rx.box(
                                rx.text(AppState.edit_selection_order_map[img_name], color="white", weight="bold", font_size="1.5em"),
                                bg="rgba(90, 40, 180, 0.75)", position="absolute", inset="0", border_radius="md",
                                display="flex", align_items="center", justify_content="center"
                            )
                        ),
                        rx.icon("x", on_click=lambda: AppState.remove_edit_uploaded_image(img_name), style={"position": "absolute", "top": "-6px", "right": "-6px", "background": "var(--red-9)", "color": "white", "border_radius": "50%", "padding": "2px", "cursor": "pointer", "width": "18px", "height": "18px"}),
                        position="relative", border="2px solid",
                        border_color=rx.cond(AppState.edit_image_selection_for_grouping.contains(img_name), "var(--violet-9)", "transparent"),
                        border_radius="lg", cursor="pointer",
                        on_click=lambda: AppState.toggle_edit_image_selection_for_grouping(img_name),
                    )
                 ),
                wrap="wrap", spacing="3", padding_top="0.5em",
             ),
            rx.button("Crear Grupo de Color", on_click=AppState.create_edit_variant_group, margin_top="0.5em", width="100%", type="button"),
            rx.divider(margin_y="1em"),
            rx.text("3. Grupos existentes:"),
            rx.flex(rx.foreach(AppState.edit_variant_groups, render_group_card), wrap="wrap", spacing="2"),
            
            # --- ✨ INICIO: AQUÍ ES DONDE SE USA EL ARGUMENTO ✨ ---
            # Inserta el componente selector que recibimos como argumento
            main_image_selector,
            # --- ✨ FIN ✨ ---
            
            spacing="3", width="100%", align_items="stretch",
        ) # Fin vstack de image_and_group_section

    def attributes_and_stock_section() -> rx.Component:
        """Sección para definir atributos y stock del grupo seleccionado en EDICIÓN."""
        # --- Define los componentes de atributos dinámicos (usando variables 'edit_') ---
        ropa_attributes = rx.vstack(
             rx.text("Talla"),
            rx.hstack(
                rx.select(LISTA_TALLAS_ROPA, placeholder="Añadir talla...", value=AppState.edit_temp_talla, on_change=AppState.set_edit_temp_talla),
                rx.button("Añadir", on_click=AppState.add_edit_variant_attribute("Talla", AppState.edit_temp_talla), type="button")
            ),
            rx.flex(
                 rx.foreach(AppState.edit_attr_tallas_ropa, lambda talla: rx.badge(talla, rx.icon("x", size=12, on_click=AppState.remove_edit_variant_attribute("Talla", talla), cursor="pointer"), variant="soft", color_scheme="gray")),
                wrap="wrap", spacing="2", min_height="28px", padding_top="0.5em"
             ),
            spacing="3", align_items="stretch", width="100%"
        )
        calzado_attributes = rx.vstack(
            rx.text("Número"),
            rx.hstack(
                rx.select(LISTA_NUMEROS_CALZADO, placeholder="Añadir número...", value=AppState.edit_temp_numero, on_change=AppState.set_edit_temp_numero),
                rx.button("Añadir", on_click=AppState.add_edit_variant_attribute("Número", AppState.edit_temp_numero), type="button")
            ),
            rx.flex(
                 rx.foreach(AppState.edit_attr_numeros_calzado, lambda num: rx.badge(num, rx.icon("x", size=12, on_click=AppState.remove_edit_variant_attribute("Número", num), cursor="pointer"), variant="soft", color_scheme="gray")),
                wrap="wrap", spacing="2", min_height="28px", padding_top="0.5em"
            ),
            spacing="3", align_items="stretch", width="100%"
        )
        mochilas_attributes = rx.vstack(
            rx.text("Tamaño"),
            rx.hstack(
                rx.select(LISTA_TAMANOS_MOCHILAS, placeholder="Añadir tamaño...", value=AppState.edit_temp_tamano, on_change=AppState.set_edit_temp_tamano),
                 rx.button("Añadir", on_click=AppState.add_edit_variant_attribute("Tamaño", AppState.edit_temp_tamano), type="button")
            ),
            rx.flex(
                 rx.foreach(AppState.edit_attr_tamanos_mochila, lambda tam: rx.badge(tam, rx.icon("x", size=12, on_click=AppState.remove_edit_variant_attribute("Tamaño", tam), cursor="pointer"), variant="soft", color_scheme="gray")),
                wrap="wrap", spacing="2", min_height="28px", padding_top="0.5em"
            ),
            spacing="3", align_items="stretch", width="100%"
        )
        # --- Fin componentes dinámicos ---

        return rx.cond(
            AppState.edit_selected_group_index >= 0,
            rx.vstack(
                 rx.divider(margin_y="1.5em"),
                rx.heading(f"4. Edición Grupo #{AppState.edit_selected_group_index + 1}", size="5"),
                rx.grid(
                    # --- Columna 1: Atributos y Fondos Lightbox ---
                    rx.vstack(
                        rx.text("Atributos del Grupo", weight="medium"),
                        rx.text("Color"),
                        searchable_select( # Selector de color
                            placeholder="Seleccionar color...", options=AppState.filtered_attr_colores,
                            on_change_select=AppState.set_edit_temp_color, value_select=AppState.edit_temp_color,
                            search_value=AppState.search_attr_color, on_change_search=AppState.set_search_attr_color,
                            filter_name="edit_color_filter"
                        ),
                         # Renderizado condicional de Talla/Número/Tamaño (usando variables 'edit_')
                        rx.cond(
                            AppState.edit_category == Category.ROPA.value, ropa_attributes,
                            rx.cond(AppState.edit_category == Category.CALZADO.value, calzado_attributes,
                                rx.cond(AppState.edit_category == Category.MOCHILAS.value, mochilas_attributes,
                                     rx.text("Selecciona una categoría válida.", color_scheme="red")
                                )
                            )
                        ),
                         rx.button("Guardar Atributos", on_click=AppState.update_edit_group_attributes, margin_top="1em", size="2", variant="outline", type="button"),

                        # --- Campos de Lightbox (usando variables 'edit_') ---
                        rx.divider(margin_y="1em"),
                        rx.text("Fondo Lightbox (Sitio Claro)", weight="medium"),
                        rx.segmented_control.root(
                             rx.segmented_control.item("Oscuro", value="dark"),
                            rx.segmented_control.item("Blanco", value="white"),
                            value=AppState.edit_temp_lightbox_bg_light,
                            on_change=AppState.set_edit_temp_lightbox_bg_light,
                             color_scheme="gray", size="1",
                        ),
                        rx.text("Fondo Lightbox (Sitio Oscuro)", weight="medium", margin_top="0.5em"),
                        rx.segmented_control.root(
                            rx.segmented_control.item("Oscuro", value="dark"),
                             rx.segmented_control.item("Blanco", value="white"),
                            value=AppState.edit_temp_lightbox_bg_dark,
                            on_change=AppState.set_edit_temp_lightbox_bg_dark,
                            color_scheme="gray", size="1",
                        ),
                         spacing="3", align_items="stretch",
                    ), # Fin vstack columna 1

                    # --- Columna 2: Variantes y Stock ---
                    rx.vstack(
                         rx.text("Variantes y Stock", weight="medium"),
                         rx.button("Generar / Actualizar Variantes", on_click=AppState.generate_edit_variants_for_group(AppState.edit_selected_group_index), type="button"),
                         rx.cond( # Lista de variantes generadas (usando variables 'edit_')
                            AppState.edit_generated_variants_map.contains(AppState.edit_selected_group_index),
                            rx.scroll_area(
                                rx.vstack(
                                     rx.foreach(
                                        AppState.edit_generated_variants_map[AppState.edit_selected_group_index],
                                        lambda variant, var_index: rx.hstack(
                                             # Muestra atributo dinámico
                                            rx.text(variant.attributes.get("Talla", variant.attributes.get("Número", variant.attributes.get("Tamaño", "N/A")))),
                                            rx.spacer(),
                                             # Botones +/- y Input de stock (usando eventos 'edit_')
                                            rx.icon_button(rx.icon("minus"), on_click=AppState.decrement_edit_variant_stock(AppState.edit_selected_group_index, var_index), size="1", type="button"),
                                            rx.input(value=variant.stock.to_string(), on_change=lambda val: AppState.set_edit_variant_stock(AppState.edit_selected_group_index, var_index, val), text_align="center", max_width="50px"),
                                            rx.icon_button(rx.icon("plus"), on_click=AppState.increment_edit_variant_stock(AppState.edit_selected_group_index, var_index), size="1", type="button"),
                                            align="center"
                                         )
                                    ),
                                    spacing="2", width="100%", padding_top="1em"
                                 ),
                                 max_height="200px", type="auto", scrollbars="vertical"
                            )
                         ),
                         spacing="3", align_items="stretch",
                    ), # Fin vstack columna 2
                    
                    columns="2", spacing="4", width="100%"
                ),
                align_items="stretch", width="100%"
            )
        ) # Fin rx.cond

    # --- Estructura principal del formulario de EDICIÓN ---
    return rx.form(
        rx.grid(
            # Columna izquierda (Imágenes y Variantes - usa variables edit_)
             rx.vstack(
                image_and_group_section(), # Ya usa las variables edit_ internamente
                attributes_and_stock_section(), # Ya usa las variables edit_ y el grid corregido
                spacing="5", width="100%",
            ),
            # Columna derecha (Detalles del Producto - usa variables edit_)
            rx.vstack(
                 rx.vstack(
                    rx.text("Título del Producto"),
                    rx.input(name="title", value=AppState.edit_post_title, on_change=AppState.set_edit_post_title, required=True, max_length=40),
                    align_items="stretch"
                ),
                # --- ✨ SECCIÓN CORREGIDA Y COMPLETA ✨ ---
                rx.grid(
                    rx.vstack(
                        rx.text("Categoría"), 
                        rx.select(
                            AppState.categories, 
                            name="category", 
                            required=True, 
                            value=AppState.edit_category, 
                            on_change=AppState.set_edit_category
                        ), 
                        align_items="stretch"
                    ),
                    rx.vstack(
                        rx.text("Tipo"), 
                        searchable_select(
                            placeholder="Selecciona un Tipo", 
                            options=AppState.edit_filtered_attr_tipos, 
                            value_select=AppState.edit_attr_tipo, 
                            on_change_select=AppState.set_edit_attr_tipo, 
                            search_value=AppState.edit_search_attr_tipo, 
                            on_change_search=AppState.set_edit_search_attr_tipo, 
                            filter_name="edit_tipo_filter", 
                            is_disabled=~AppState.edit_category
                        ), 
                        align_items="stretch"
                    ),
                    rx.vstack(
                        rx.text(AppState.edit_material_label),
                        searchable_select(
                            placeholder=rx.cond(
                                AppState.edit_category, 
                                f"Selecciona {AppState.edit_material_label}", 
                                "Elige categoría"
                            ), 
                            options=AppState.edit_filtered_attr_materiales, 
                            value_select=AppState.edit_attr_material, 
                            on_change_select=AppState.set_edit_attr_material, 
                            search_value=AppState.edit_search_attr_material, 
                            on_change_search=AppState.set_edit_search_attr_material, 
                            filter_name="edit_material_filter", 
                            is_disabled=~AppState.edit_category
                        ), 
                        align_items="stretch"
                    ),
                    columns={"initial": "1", "md": "3"},
                    spacing="4", 
                    width="100%"
                ),
                # --- ✨ FIN DE LA SECCIÓN CORREGIDA ✨ ---
                
                # Resto de campos (Precio, Ganancia, IVA, Origen, Envío, etc. - usan variables edit_)
                rx.grid(
                    rx.vstack(rx.text("Precio (COP)"), rx.input(name="price", value=AppState.edit_price_str, on_change=AppState.set_edit_price_str, on_blur=AppState.validate_price_on_blur_edit, type="number", required=True), align_items="stretch"),
                    rx.vstack(rx.text("Ganancia (COP)"), rx.input(name="profit", value=AppState.edit_profit_str, on_change=AppState.set_edit_profit_str, on_blur=AppState.validate_profit_on_blur_edit, type="number"), align_items="stretch"),
                    columns="2", spacing="4", width="100%"
                ),
                rx.grid(
                     rx.vstack(rx.text("Incluye IVA (19%)"), rx.hstack(rx.switch(name="price_includes_iva", is_checked=AppState.edit_price_includes_iva, on_change=AppState.set_edit_price_includes_iva), rx.text(rx.cond(AppState.edit_price_includes_iva, "Sí", "No")))),
                    rx.vstack(rx.text("Origen"), rx.hstack(rx.switch(name="is_imported", is_checked=AppState.edit_is_imported, on_change=AppState.set_edit_is_imported), rx.text(rx.cond(AppState.edit_is_imported, "Importado", "Nacional")))),
                    columns="2", spacing="4", width="100%"
                ),
                rx.grid(
                    rx.vstack(rx.text("Costo de Envío Mínimo (Local)"), rx.input(name="edit_shipping_cost_str", value=AppState.edit_shipping_cost_str, on_change=AppState.set_edit_shipping_cost_str, placeholder="Ej: 3000"), rx.text("El costo final aumentará según la distancia.", size="1", color_scheme="gray"), align_items="stretch"),
                    rx.vstack(rx.text("Moda Completa"), rx.hstack(rx.switch(name="edit_is_moda_completa", is_checked=AppState.edit_is_moda_completa, on_change=AppState.set_edit_is_moda_completa), rx.text(rx.cond(AppState.edit_is_moda_completa, "Activo", "Inactivo"))), rx.input(value=AppState.edit_free_shipping_threshold_str, on_change=AppState.set_edit_free_shipping_threshold_str, is_disabled=~AppState.edit_is_moda_completa, placeholder="Monto para envío gratis"), rx.text("Envío gratis en compras > este monto.", size="1", color_scheme="gray"), align_items="stretch"),
                    rx.vstack(rx.text("Envío Combinado"), rx.hstack(rx.switch(name="combines_shipping", is_checked=AppState.edit_combines_shipping, on_change=AppState.set_edit_combines_shipping), rx.text(rx.cond(AppState.edit_combines_shipping, "Activo", "Inactivo"))), rx.text("Permite que varios productos usen un solo envío.", size="1", color_scheme="gray"), align_items="stretch"),
                    rx.vstack(rx.text("Límite de Productos"), rx.input(name="edit_shipping_combination_limit_str", value=AppState.edit_shipping_combination_limit_str, on_change=AppState.set_edit_shipping_combination_limit_str, is_disabled=~AppState.edit_combines_shipping, placeholder="Máx. de items por envío"), rx.text("Máx. de items por envío combinado.", size="1", color_scheme="gray"), align_items="stretch"),
                     columns="2", spacing="4", width="100%",
                ),
                rx.vstack(
                    rx.text("Descripción"),
                    rx.text_area(name="content", value=AppState.edit_post_content, on_change=AppState.set_edit_post_content, style={"height": "120px"}),
                    align_items="stretch",
                ),
                 spacing="4", align_items="stretch", width="100%",
            ),
            columns={"initial": "1", "md": "500px 1fr"}, spacing="6", width="100%", align_items="start",
        ),
        # Botones de acción (Eliminar y Guardar)
        rx.hstack(
            rx.alert_dialog.root( # Botón Eliminar
                rx.alert_dialog.trigger(rx.button("Eliminar Publicación", color_scheme="red", variant="soft", type="button")),
                rx.alert_dialog.content(
                     rx.alert_dialog.title("Confirmar Eliminación"),
                    rx.alert_dialog.description("Esta acción no se puede deshacer."),
                    rx.flex(
                        rx.alert_dialog.cancel(rx.button("Cancelar", variant="soft", color_scheme="gray")),
                        rx.alert_dialog.action(rx.button("Sí, Eliminar", on_click=AppState.delete_post(AppState.post_to_edit_id), color_scheme="red")),
                         spacing="3", margin_top="1em", justify="end",
                    ),
                ),
            ),
            rx.spacer(),
            # Botón Guardar Cambios (llama al evento directamente)
            rx.button("Guardar Cambios", on_click=AppState.save_edited_post, size="3", color_scheme="violet"),
            justify="between", align="center", width="100%", margin_top="1.5em",
        ),
        
        width="100%",
    ) # Fin del rx.form