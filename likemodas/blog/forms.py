# En: likemodas/blog/forms.py (VERSIÓN COMPLETA Y CORREGIDA)

import reflex as rx
from ..state import AppState, VariantGroupDTO, VariantFormData
from ..models import Category
from ..ui.components import searchable_select
from ..data.product_options import LISTA_COLORES, LISTA_TALLAS_ROPA

# =============================================================================
# FORMULARIO PARA CREAR PUBLICACIONES (COMPLETO)
# =============================================================================
def blog_post_add_form() -> rx.Component:
    """
    Formulario para AÑADIR una nueva publicación.
    """
    # --- Componentes internos de la UI ---
    def image_and_group_section() -> rx.Component:
        """
        Componente de UI para la gestión de imágenes. Permite subir, seleccionar,
        ordenar numéricamente y agrupar imágenes para crear variantes de productos.
        """
        def render_group_card(group: VariantGroupDTO, index: rx.Var[int]) -> rx.Component:
            """Renderiza una tarjeta para un grupo de variantes ya creado."""
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
                    on_click=AppState.remove_variant_group(index),
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
                on_click=AppState.select_group_for_editing(index),
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
                        rx.image(src=rx.get_upload_url(img_name), width="60px", height="60px", object_fit="cover", border_radius="md"),
                        
                        # --- Lógica para mostrar el orden numérico y las flechas ---
                        rx.cond(
                            AppState.image_selection_for_grouping.contains(img_name),
                            rx.box(
                                # Muestra el número de orden usando el mapa computado
                                rx.text(
                                    AppState.selection_order_map[img_name],
                                    color="white", weight="bold", font_size="1.2em",
                                ),
                                # Flechas para reordenar la selección
                                rx.hstack(
                                    rx.icon("arrow-left", size=14, on_click=AppState.move_image_in_selection(img_name, -1), cursor="pointer", _hover={"color": "var(--violet-9)"}),
                                    rx.icon("arrow-right", size=14, on_click=AppState.move_image_in_selection(img_name, 1), cursor="pointer", _hover={"color": "var(--violet-9)"}),
                                    spacing="1",
                                    position="absolute", bottom="2px", left="50%",
                                    transform="translateX(-50%)", bg="rgba(255, 255, 255, 0.7)",
                                    border_radius="sm", padding="0 2px",
                                ),
                                bg="rgba(90, 40, 180, 0.7)", 
                                position="absolute", inset="0", border_radius="md",
                                display="flex", align_items="center", justify_content="center"
                            )
                        ),
                        
                        # Icono para eliminar una imagen individual de la subida
                        rx.icon(
                            "x",
                            on_click=AppState.remove_uploaded_image(img_name),
                            style={
                                "position": "absolute", "top": "-5px", "right": "-5px",
                                "background": "var(--red-9)", "color": "white",
                                "border_radius": "50%", "padding": "1px", "cursor": "pointer",
                                "width": "16px", "height": "16px"
                            }
                        ),
                        position="relative",
                        border="2px solid",
                        border_color=rx.cond(AppState.image_selection_for_grouping.contains(img_name), "var(--violet-9)", "transparent"),
                        border_radius="lg", cursor="pointer",
                        on_click=AppState.toggle_image_selection_for_grouping(img_name),
                    )
                ),
                wrap="wrap", spacing="2", padding_top="0.25em",
            ),
            rx.button(
                "Crear Grupo de Color",
                on_click=AppState.create_variant_group,
                margin_top="0.5em", width="100%",
                type="button",
            ),
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
                        searchable_select(placeholder="Seleccionar color...", options=AppState.filtered_attr_colores, on_change_select=AppState.set_temp_color, value_select=AppState.temp_color, search_value=AppState.search_attr_color, on_change_search=AppState.set_search_attr_color, filter_name="color_filter_main"),
                        rx.text("Talla"),
                        rx.hstack(
                            rx.select(LISTA_TALLAS_ROPA, placeholder="Añadir talla...", value=AppState.temp_talla, on_change=AppState.set_temp_talla),
                            rx.button("Añadir", on_click=AppState.add_variant_attribute("Talla", AppState.temp_talla), type="button")
                        ),
                        rx.flex(
                             rx.foreach(
                                AppState.attr_tallas_ropa,
                                lambda talla: rx.badge(talla, rx.icon("x", size=12, on_click=AppState.remove_variant_attribute("Talla", talla), cursor="pointer"), variant="soft", color_scheme="gray")
                             ),
                            wrap="wrap", spacing="2", min_height="28px", padding_top="0.5em"
                        ),
                        rx.button("Guardar Atributos", on_click=AppState.update_group_attributes, margin_top="1em", size="2", variant="outline", type="button"),
                        spacing="3", align_items="stretch",
                    ),
                    rx.vstack(
                        rx.text("Variantes y Stock", weight="medium"),
                        rx.button("Generar / Actualizar Variantes", on_click=AppState.generate_variants_for_group(AppState.selected_group_index), type="button"),
                        rx.cond(
                            AppState.generated_variants_map.contains(AppState.selected_group_index),
                            rx.scroll_area(
                                rx.vstack(
                                     rx.foreach(
                                        AppState.generated_variants_map[AppState.selected_group_index],
                                        lambda variant, var_index: rx.hstack(
                                            rx.text(variant.attributes.get("Talla", "N/A")), rx.spacer(),
                                            rx.icon_button(rx.icon("minus"), on_click=AppState.decrement_variant_stock(AppState.selected_group_index, var_index), size="1", type="button"),
                                            rx.input(value=variant.stock.to_string(), on_change=lambda val: AppState.set_variant_stock(AppState.selected_group_index, var_index, val), text_align="center", max_width="50px"),
                                            rx.icon_button(rx.icon("plus"), on_click=AppState.increment_variant_stock(AppState.selected_group_index, var_index), size="1", type="button"),
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
            # Columna izquierda
            rx.vstack(
                image_and_group_section(),
                attributes_and_stock_section(),
                spacing="5",
                width="100%",
            ),
            # Columna derecha
            rx.vstack(
                rx.vstack(
                    rx.text("Título del Producto"), 
                    rx.input(name="title", value=AppState.title, on_change=AppState.set_title, required=True, max_length=24), 
                    align_items="stretch"
                ),
                rx.vstack(rx.text("Categoría"), rx.select(AppState.categories, value=AppState.category, on_change=AppState.set_category, name="category", required=True), align_items="stretch"),
                rx.grid(
                    rx.vstack(rx.text("Precio (COP)"), rx.input(name="price", value=AppState.price_str, on_change=AppState.set_price_str, type="number", required=True, placeholder="Ej: 55000")),
                    rx.vstack(rx.text("Ganancia (COP)"), rx.input(name="profit", value=AppState.profit_str, on_change=AppState.set_profit_str, type="number", placeholder="Ej: 15000")),
                    columns="2", spacing="4"
                ),
                rx.grid(
                    rx.vstack(rx.text("Incluye IVA (19%)"), rx.hstack(rx.switch(is_checked=AppState.price_includes_iva, on_change=AppState.set_price_includes_iva), rx.text(rx.cond(AppState.price_includes_iva, "Sí", "No")))),
                    rx.vstack(rx.text("Origen"), rx.hstack(rx.switch(is_checked=AppState.is_imported, on_change=AppState.set_is_imported), rx.text(rx.cond(AppState.is_imported, "Importado", "Nacional")))),
                    columns="2", spacing="4"
                ),
                rx.grid(
                    rx.vstack(
                        rx.text("Costo de Envío Mínimo (Local)"), 
                        rx.input(value=AppState.shipping_cost_str, on_change=AppState.set_shipping_cost_str, placeholder="Ej: 3000"), 
                        rx.text("El costo final aumentará según la distancia.", size="1", color_scheme="gray"), 
                        align_items="stretch"
                    ),
                    rx.vstack(
                        rx.text("Moda Completa"), 
                        rx.hstack(rx.switch(is_checked=AppState.is_moda_completa, on_change=AppState.set_is_moda_completa), rx.text(rx.cond(AppState.is_moda_completa, "Activo", "Inactivo"))), 
                        rx.input(value=AppState.free_shipping_threshold_str, on_change=AppState.set_free_shipping_threshold_str, is_disabled=~AppState.is_moda_completa, placeholder="Monto para envío gratis"), 
                        rx.text("Envío gratis en compras > este monto.", size="1", color_scheme="gray"), 
                        align_items="stretch"
                    ),
                    rx.vstack(
                        rx.text("Envío Combinado"), 
                        rx.hstack(rx.switch(is_checked=AppState.combines_shipping, on_change=AppState.set_combines_shipping), rx.text(rx.cond(AppState.combines_shipping, "Activo", "Inactivo"))), 
                        rx.text("Permite que varios productos usen un solo envío.", size="1", color_scheme="gray"), 
                        align_items="stretch"
                    ),
                    rx.vstack(
                        rx.text("Límite de Productos"), 
                        rx.input(value=AppState.shipping_combination_limit_str, on_change=AppState.set_shipping_combination_limit_str, is_disabled=~AppState.combines_shipping, placeholder="Máx. de items por envío"), 
                        rx.text("Máx. de items por envío combinado.", size="1", color_scheme="gray"), 
                        align_items="stretch"
                    ),
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
        spacing="5",
        width="100%",
    )


# =============================================================================
# FORMULARIO DE EDICIÓN (COMPLETAMENTE RECONSTRUIDO Y CORREGIDO)
# =============================================================================
def blog_post_edit_form() -> rx.Component:
    """
    [NUEVA VERSIÓN] Formulario para EDITAR una publicación, ahora con toda la 
    funcionalidad de grupos, variantes, stock y estilos, y campos completos.
    """
    def image_and_group_section() -> rx.Component:
        def render_group_card(group: VariantGroupDTO, index: rx.Var[int]) -> rx.Component:
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
            rx.text("2. Selecciona imágenes para crear un grupo:"),
            rx.flex(
                 rx.foreach(
                    AppState.edit_uploaded_images,
                    lambda img_name: rx.box(
                        rx.image(src=rx.get_upload_url(img_name), width="60px", height="60px", object_fit="cover", border_radius="md"),
                        rx.cond(
                            AppState.edit_image_selection_for_grouping.contains(img_name),
                            rx.box(
                                rx.text(
                                    AppState.edit_image_selection_for_grouping.index(img_name) + 1,
                                    color="white", weight="bold", font_size="1.2em",
                                ),
                                rx.hstack(
                                    rx.icon("arrow-left", size=14, on_click=AppState.move_edit_image_in_selection(img_name, -1), cursor="pointer"),
                                    rx.icon("arrow-right", size=14, on_click=AppState.move_edit_image_in_selection(img_name, 1), cursor="pointer"),
                                    spacing="1", position="absolute", bottom="2px", left="50%", transform="translateX(-50%)",
                                    bg="rgba(255, 255, 255, 0.7)", border_radius="sm", padding="0 2px",
                                ),
                                bg="rgba(90, 40, 180, 0.7)", position="absolute", inset="0", border_radius="md",
                                display="flex", align_items="center", justify_content="center"
                            )
                        ),
                        rx.icon("x", on_click=AppState.remove_edit_uploaded_image(img_name), style={"position": "absolute", "top": "-5px", "right": "-5px", "background": "var(--red-9)", "color": "white", "border_radius": "50%", "padding": "1px", "cursor": "pointer", "width": "16px", "height": "16px"}),
                        position="relative", border="2px solid",
                        border_color=rx.cond(AppState.edit_image_selection_for_grouping.contains(img_name), "var(--violet-9)", "transparent"),
                        border_radius="lg", cursor="pointer",
                        on_click=AppState.toggle_edit_image_selection_for_grouping(img_name),
                    )
                ),
                wrap="wrap", spacing="2", padding_top="0.25em",
             ),
            rx.button("Crear Grupo de Color", on_click=AppState.create_edit_variant_group, margin_top="0.5em", width="100%", type="button"),
            rx.divider(margin_y="1em"),
            rx.text("3. Grupos existentes:"),
            rx.flex(rx.foreach(AppState.edit_variant_groups, render_group_card), wrap="wrap", spacing="2"),
            spacing="3", width="100%", align_items="stretch",
        )

    def attributes_and_stock_section() -> rx.Component:
        return rx.cond(
             AppState.edit_selected_group_index >= 0,
            rx.vstack(
                rx.divider(margin_y="1.5em"),
                rx.heading(f"4. Edición Grupo #{AppState.edit_selected_group_index + 1}", size="5"),
                rx.grid(
                    rx.vstack(
                        rx.text("Atributos del Grupo", weight="medium"),
                        rx.text("Color"),
                        searchable_select(placeholder="Seleccionar color...", options=AppState.filtered_attr_colores, on_change_select=AppState.set_edit_temp_color, value_select=AppState.edit_temp_color, search_value=AppState.search_attr_color, on_change_search=AppState.set_search_attr_color, filter_name="edit_color_filter"),
                        rx.text("Talla"),
                        rx.hstack(
                            rx.select(LISTA_TALLAS_ROPA, placeholder="Añadir talla...", value=AppState.edit_temp_talla, on_change=AppState.set_edit_temp_talla),
                            rx.button("Añadir", on_click=AppState.add_edit_variant_attribute("Talla", AppState.edit_temp_talla), type="button")
                        ),
                        rx.flex(
                             rx.foreach(AppState.edit_attr_tallas_ropa, lambda talla: rx.badge(talla, rx.icon("x", size=12, on_click=AppState.remove_edit_variant_attribute("Talla", talla), cursor="pointer"), variant="soft", color_scheme="gray")),
                            wrap="wrap", spacing="2", min_height="28px", padding_top="0.5em"
                        ),
                        rx.button("Guardar Atributos", on_click=AppState.update_edit_group_attributes, margin_top="1em", size="2", variant="outline", type="button"),
                        spacing="3", align_items="stretch",
                    ),
                    rx.vstack(
                        rx.text("Variantes y Stock", weight="medium"),
                        rx.button("Generar / Actualizar Variantes", on_click=AppState.generate_edit_variants_for_group(AppState.edit_selected_group_index), type="button"),
                        rx.cond(
                            AppState.edit_generated_variants_map.contains(AppState.edit_selected_group_index),
                            rx.scroll_area(
                                rx.vstack(
                                     rx.foreach(
                                        AppState.edit_generated_variants_map[AppState.edit_selected_group_index],
                                        lambda variant, var_index: rx.hstack(
                                            rx.text(variant.attributes.get("Talla", "N/A")), rx.spacer(),
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
                    ),
                    columns="2", spacing="4", width="100%"
                ),
                align_items="stretch", width="100%"
            )
        )

    return rx.form(
        rx.grid(
            rx.vstack(
                image_and_group_section(),
                attributes_and_stock_section(),
                spacing="5", width="100%",
            ),
            rx.vstack(
                rx.vstack(rx.text("Título del Producto"), rx.input(name="title", value=AppState.edit_post_title, on_change=AppState.set_edit_post_title, required=True, max_length=24), align_items="stretch"),
                rx.vstack(rx.text("Categoría"), rx.select(AppState.categories, value=AppState.edit_category, on_change=AppState.set_edit_category, name="category", required=True), align_items="stretch"),
                rx.grid(
                    rx.vstack(rx.text("Precio (COP)"), rx.input(name="price", value=AppState.edit_price_str, on_change=AppState.set_edit_price_str, type="number", required=True)),
                    rx.vstack(rx.text("Ganancia (COP)"), rx.input(name="profit", value=AppState.edit_profit_str, on_change=AppState.set_edit_profit_str, type="number")),
                    columns="2", spacing="4"
                ),
                rx.grid(
                    rx.vstack(rx.text("Incluye IVA (19%)"), rx.hstack(rx.switch(is_checked=AppState.edit_price_includes_iva, on_change=AppState.set_edit_price_includes_iva), rx.text(rx.cond(AppState.edit_price_includes_iva, "Sí", "No")))),
                    rx.vstack(rx.text("Origen"), rx.hstack(rx.switch(is_checked=AppState.edit_is_imported, on_change=AppState.set_edit_is_imported), rx.text(rx.cond(AppState.edit_is_imported, "Importado", "Nacional")))),
                    columns="2", spacing="4"
                ),
                rx.grid(
                    rx.vstack(
                        rx.text("Costo de Envío Mínimo (Local)"), 
                        rx.input(name="edit_shipping_cost_str", value=AppState.edit_shipping_cost_str, on_change=AppState.set_edit_shipping_cost_str, placeholder="Ej: 3000"), 
                        rx.text("El costo final aumentará según la distancia.", size="1", color_scheme="gray"), 
                        align_items="stretch"
                    ),
                    rx.vstack(
                        rx.text("Moda Completa"), 
                        rx.hstack(rx.switch(is_checked=AppState.edit_is_moda_completa, on_change=AppState.set_edit_is_moda_completa), rx.text(rx.cond(AppState.edit_is_moda_completa, "Activo", "Inactivo"))), 
                        rx.input(value=AppState.edit_free_shipping_threshold_str, on_change=AppState.set_edit_free_shipping_threshold_str, is_disabled=~AppState.edit_is_moda_completa, placeholder="Monto para envío gratis"), 
                        rx.text("Envío gratis en compras > este monto.", size="1", color_scheme="gray"), 
                        align_items="stretch"
                    ),
                    rx.vstack(
                        rx.text("Envío Combinado"), 
                        rx.hstack(rx.switch(is_checked=AppState.edit_combines_shipping, on_change=AppState.set_edit_combines_shipping), rx.text(rx.cond(AppState.edit_combines_shipping, "Activo", "Inactivo"))), 
                        rx.text("Permite que varios productos usen un solo envío.", size="1", color_scheme="gray"), 
                        align_items="stretch"
                    ),
                    rx.vstack(
                        rx.text("Límite de Productos"), 
                        rx.input(value=AppState.edit_shipping_combination_limit_str, on_change=AppState.set_edit_shipping_combination_limit_str, is_disabled=~AppState.edit_combines_shipping, placeholder="Máx. de items por envío"), 
                        rx.text("Máx. de items por envío combinado.", size="1", color_scheme="gray"), 
                        align_items="stretch"
                    ),
                    columns="2", spacing="4", width="100%",
                ),
                rx.vstack(
                    rx.text("Descripción"),
                    rx.text_area(name="content", value=AppState.edit_post_content, on_change=AppState.set_edit_post_content, style={"height": "120px"}),
                    align_items="stretch",
                ),
                spacing="4", align_items="stretch", width="100%",
            ),
            columns={"initial": "1", "md": "2"}, spacing="6", width="100%",
        ),
        rx.hstack(
            rx.alert_dialog.root(
                rx.alert_dialog.trigger(rx.button("Eliminar Publicación", color_scheme="red", variant="soft", type="button")),
                rx.alert_dialog.content(
                    rx.alert_dialog.title("Confirmar Eliminación"),
                    rx.alert_dialog.description("Esta acción no se puede deshacer y eliminará el producto permanentemente."),
                    rx.flex(
                        rx.alert_dialog.cancel(rx.button("Cancelar", variant="soft", color_scheme="gray")),
                        rx.alert_dialog.action(rx.button("Sí, Eliminar Permanentemente", on_click=AppState.delete_post(AppState.post_to_edit_id), color_scheme="red")),
                        spacing="3", margin_top="1em", justify="end",
                    ),
                ),
            ),
            rx.spacer(),
            rx.button("Guardar Cambios", type="submit", size="3", color_scheme="violet"),
            justify="between", align="center", width="100%", margin_top="1.5em",
        ),
        on_submit=AppState.save_edited_post,
        width="100%",
    )