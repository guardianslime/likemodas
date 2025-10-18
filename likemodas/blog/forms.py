# likemodas/blog/forms.py 

import reflex as rx
from ..state import AppState, VariantGroupDTO
from ..models import Category
from ..ui.components import searchable_select
from ..data.product_options import LISTA_COLORES, LISTA_TALLAS_ROPA

def blog_post_add_form() -> rx.Component:
    """
    [VERSIÓN 3.2] Formulario con ancho máximo reducido y límite de caracteres en el título.
    """
    def image_and_group_section() -> rx.Component:
        # (Esta función interna no tiene cambios)
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
                border_width="2px",
                border_color=rx.cond(is_selected, "var(--violet-9)", "transparent"),
                padding="0.25em", border_radius="md", cursor="pointer",
                on_click=AppState.select_group_for_editing(index),
            )

        return rx.vstack(
            rx.text("1. Subir Imágenes (máx 5)", weight="bold"),
            rx.upload(
                rx.vstack(rx.icon("upload"), rx.text("Arrastra o haz clic")),
                id="blog_upload", multiple=True, max_files=5,
                on_drop=AppState.handle_add_upload(rx.upload_files("blog_upload")),
                border="1px dashed var(--gray-a6)", padding="2em", width="100%"
            ),
            rx.text("2. Selecciona imágenes para crear un grupo de color:"),
            rx.flex(
                rx.foreach(
                    AppState.uploaded_images,
                    lambda img_name: rx.box(
                        rx.image(src=rx.get_upload_url(img_name), width="60px", height="60px", object_fit="cover", border_radius="md"),
                        rx.cond(
                            AppState.image_selection_for_grouping.contains(img_name),
                            rx.box(
                                rx.icon("check", color="white", size=18),
                                bg="rgba(90, 40, 180, 0.7)", position="absolute", inset="0", border_radius="md",
                                display="flex", align_items="center", justify_content="center"
                            )
                        ),
                        border="2px solid",
                        border_color=rx.cond(AppState.image_selection_for_grouping.contains(img_name), "var(--violet-9)", "transparent"),
                        border_radius="lg", cursor="pointer", position="relative",
                        on_click=AppState.toggle_image_selection_for_grouping(img_name),
                    )
                ),
                wrap="wrap", spacing="2", padding_top="0.25em",
            ),
            rx.button("Crear Grupo de Color", on_click=AppState.create_variant_group, margin_top="0.5em", width="100%"),
            rx.divider(margin_y="1em"),
            rx.text("3. Grupos (Selecciona uno para editar abajo):"),
            rx.flex(rx.foreach(AppState.variant_groups, render_group_card), wrap="wrap", spacing="2"),
            spacing="3", width="100%", align_items="stretch",
        )

    def attributes_and_stock_section() -> rx.Component:
        # (Esta función interna no tiene cambios)
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
                            rx.button("Añadir", on_click=AppState.add_variant_attribute("Talla", AppState.temp_talla))
                        ),
                        rx.flex(
                            rx.foreach(
                                AppState.attr_tallas_ropa,
                                lambda talla: rx.badge(talla, rx.icon("x", size=12, on_click=AppState.remove_variant_attribute("Talla", talla), cursor="pointer"), variant="soft", color_scheme="gray")
                            ),
                            wrap="wrap", spacing="2", min_height="28px", padding_top="0.5em"
                        ),
                        rx.button("Guardar Atributos", on_click=AppState.update_group_attributes, margin_top="1em", size="2", variant="outline"),
                        spacing="3", align_items="stretch",
                    ),
                    rx.vstack(
                        rx.text("Variantes y Stock", weight="medium"),
                        rx.text("Genera combinaciones y asigna stock.", size="2", color_scheme="gray"),
                        rx.button("Generar / Actualizar Variantes", on_click=AppState.generate_variants_for_group(AppState.selected_group_index)),
                        rx.cond(
                            AppState.generated_variants_map.contains(AppState.selected_group_index),
                            rx.scroll_area(
                                rx.vstack(
                                    rx.foreach(
                                        AppState.generated_variants_map[AppState.selected_group_index],
                                        lambda variant, var_index: rx.hstack(
                                            rx.text(variant.attributes["Talla"]), rx.spacer(),
                                            rx.icon_button(rx.icon("minus"), on_click=AppState.decrement_variant_stock(AppState.selected_group_index, var_index), size="1"),
                                            rx.input(value=variant.stock.to_string(), on_change=lambda val: AppState.set_variant_stock(AppState.selected_group_index, var_index, val), text_align="center", max_width="50px"),
                                            rx.icon_button(rx.icon("plus"), on_click=AppState.increment_variant_stock(AppState.selected_group_index, var_index), size="1"),
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
        rx.vstack(
            rx.grid(
                rx.vstack(
                    image_and_group_section(),
                    attributes_and_stock_section(),
                    spacing="5",
                    width="100%",
                ),
                rx.vstack(
                    # --- ✨ INICIO: LÍMITE DE CARACTERES PARA EL TÍTULO ✨ ---
                    rx.vstack(
                        rx.text("Título del Producto"), 
                        rx.input(
                            name="title", 
                            value=AppState.title, 
                            on_change=AppState.set_title, 
                            required=True,
                            max_length=60  # <-- Límite añadido
                        ), 
                        align_items="stretch"
                    ),
                    # --- ✨ FIN ✨ ---
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
                columns={"initial": "1", "lg": "2"}, 
                spacing="6", 
                width="100%", 
                align_items="start",
            ),
            rx.hstack(
                rx.spacer(),
                rx.button("Publicar Producto", type="submit", color_scheme="violet", size="3"),
                width="100%", 
                margin_top="1em"
            ),
            spacing="5", 
            width="100%",
            # --- ✨ CORRECCIÓN DE ANCHO MÁXIMO ✨ ---
            max_width="700px", 
        ),
        on_submit=AppState.submit_and_publish,
        reset_on_submit=True,
        width="100%", 
    )


# --- ⚠️ INICIO: FORMULARIO DE EDICIÓN (NO FUNCIONAL CON GRUPOS AÚN) ⚠️ ---
# Nota: Este es el código original del formulario de edición.
# Se incluye para que el archivo esté completo, pero necesita ser refactorizado
# para soportar la nueva lógica de grupos de imágenes.

def attribute_editor_edit(
    title: str,
    options_list: list[str],
    temp_value_var: rx.Var[str],
    temp_value_setter: rx.event.EventSpec,
    add_handler: rx.event.EventHandler,
    remove_handler: rx.event.EventHandler,
    current_selections: rx.Var[list[str]],
) -> rx.Component:
    """Un componente para añadir y quitar atributos específicos a una variante en el form de edición."""
    return rx.vstack(
        rx.text(title, weight="bold", size="3"),
        rx.flex(
            rx.foreach(
                current_selections,
                lambda item: rx.badge(
                    item,
                    rx.icon("x", size=12, cursor="pointer", on_click=lambda: remove_handler(item), margin_left="0.25em"),
                    variant="soft", color_scheme="gray", size="2",
                ),
            ),
            wrap="wrap", spacing="2", min_height="36px",
        ),
        rx.hstack(
            rx.select(
                options_list, placeholder=f"Seleccionar {title.lower()}...",
                value=temp_value_var, on_change=temp_value_setter,
            ),
            rx.button("Añadir", on_click=add_handler, type="button", color_scheme="violet", variant="soft"),
            width="100%"
        ),
        align_items="stretch", width="100%", spacing="2"
    )

def variant_stock_manager_edit() -> rx.Component:
    """Componente para gestionar el stock de las variantes generadas en el form de EDICIÓN."""
    return rx.vstack(
        rx.heading("Gestión de Variantes y Stock", size="4", margin_top="1em"),
        rx.text("Genera o actualiza combinaciones y asigna su stock.", size="2", color_scheme="gray"),
        rx.button("Generar / Actualizar Variantes", on_click=AppState.generate_edit_variants, margin_y="1em", type="button", color_scheme="violet"),
        rx.cond(
            (AppState.edit_selected_image_index >= 0) & AppState.edit_variants_map.contains(AppState.edit_selected_image_index),
            rx.vstack(
                rx.foreach(
                    AppState.edit_variants_map.get(AppState.edit_selected_image_index, []),
                    lambda variant, index: rx.box(
                        rx.hstack(
                            rx.vstack(
                                rx.foreach(variant.attributes.items(), lambda item: rx.text(f"{item[0]}: ", rx.text.strong(item[1]))),
                                align_items="start", flex_grow=1,
                            ),
                            rx.hstack(
                                rx.icon_button(rx.icon("minus"), on_click=AppState.decrement_edit_variant_stock(AppState.edit_selected_image_index, index), type="button"),
                                rx.input(
                                    value=variant.stock.to_string(),
                                    on_change=lambda val: AppState.set_edit_variant_stock(AppState.edit_selected_image_index, index, val),
                                    text_align="center", max_width="70px",
                                ),
                                rx.icon_button(rx.icon("plus"), on_click=AppState.increment_edit_variant_stock(AppState.edit_selected_image_index, index), type="button"),
                                align="center", spacing="2",
                            ),
                            spacing="4", align="center", width="100%",
                        ),
                        padding="0.75em", border="1px solid", border_color=rx.color("gray", 6), border_radius="md", width="100%",
                    )
                ),
                spacing="3", width="100%",
            )
        ),
        align_items="stretch", width="100%",
    )

def blog_post_edit_form() -> rx.Component:
    """El formulario original para editar una publicación."""
    caracteristicas_ropa_edit = attribute_editor_edit(
        title="Talla", options_list=LISTA_TALLAS_ROPA,
        temp_value_var=AppState.edit_temp_talla,
        temp_value_setter=AppState.set_edit_temp_talla,
        add_handler=lambda: AppState.add_edit_variant_attribute("Talla", AppState.edit_temp_talla),
        remove_handler=lambda val: AppState.remove_edit_variant_attribute("Talla", val),
        current_selections=AppState.edit_attr_tallas_ropa,
    )

    return rx.form(
        rx.vstack(
            rx.grid(
                rx.vstack(
                    rx.text("Imágenes del Producto", as_="div", size="2", weight="bold", margin_bottom="0.5em"),
                    rx.flex(
                        rx.foreach(
                            AppState.unique_edit_form_images,
                            lambda img_url, index: rx.box(
                                rx.image(src=rx.get_upload_url(img_url), width="80px", height="80px", object_fit="cover", border_radius="md"),
                                rx.icon_button(
                                    rx.icon("trash-2", size=14),
                                    on_click=AppState.remove_edit_image(img_url),
                                    color_scheme="red", variant="soft", size="1",
                                    style={"position": "absolute", "top": "2px", "right": "2px", "cursor": "pointer", "z_index": "10"}
                                ),
                                border_width=rx.cond(AppState.edit_selected_image_index == index, "3px", "1px"),
                                border_color=rx.cond(AppState.edit_selected_image_index == index, "violet", "gray"),
                                padding="2px", border_radius="lg", cursor="pointer",
                                on_click=AppState.select_edit_image_for_editing(index),
                                position="relative",
                            )
                        ),
                        wrap="wrap", spacing="3",
                    ),
                    rx.upload(
                        rx.vstack(rx.icon("upload", size=24), rx.text("Añadir", size="2")),
                        id="edit_upload", multiple=True, max_files=5,
                        on_drop=AppState.handle_edit_upload(rx.upload_files("edit_upload")),
                        border="2px dashed #ccc", padding="1em", width="100%", margin_top="1em"
                    ),
                    rx.divider(margin_y="1em"),
                    rx.cond(
                        AppState.edit_selected_image_index >= 0,
                        rx.vstack(
                            rx.text("Atributos de Imagen Seleccionada", size="2", weight="bold"),
                            rx.text("Color", size="3"),
                            rx.select(
                                LISTA_COLORES, placeholder="Seleccionar color...", name="color",
                                value=AppState.edit_attr_colores, on_change=AppState.set_edit_attr_colores,
                            ),
                            rx.cond(AppState.edit_category == Category.ROPA.value, caracteristicas_ropa_edit),
                            rx.divider(margin_y="1em"),
                            variant_stock_manager_edit(),
                            spacing="2", align_items="stretch", width="100%"
                        )
                    ),
                    spacing="2", align_items="stretch",
                ),
                rx.vstack(
                    rx.text("Título del Producto", as_="div", size="2", weight="bold"),
                    rx.input(name="title", value=AppState.edit_post_title, on_change=AppState.set_edit_post_title, required=True, size="3"),
                    rx.text("Categoría", as_="div", size="2", weight="bold"),
                    rx.select(
                        AppState.categories, placeholder="Selecciona una categoría...", name="category",
                        value=AppState.edit_category, on_change=AppState.set_edit_category, required=True, size="3",
                    ),
                    rx.grid(
                        rx.vstack(
                            rx.text("Precio (COP)", as_="div", size="2", weight="bold"),
                            rx.input(name="price", value=AppState.edit_price_str, on_change=AppState.set_edit_price_str, type="number", required=True, size="3"),
                        ),
                        rx.vstack(
                            rx.text("Ganancia (COP)", as_="div", size="2", weight="bold"),
                            rx.input(name="profit", value=AppState.edit_profit_str, on_change=AppState.set_edit_profit_str, type="number", size="3"),
                        ),
                        columns="2", spacing="3", width="100%",
                    ),
                    rx.grid(
                        rx.vstack(rx.text("Incluye IVA"), rx.hstack(rx.switch(name="price_includes_iva", is_checked=AppState.edit_price_includes_iva, on_change=AppState.set_edit_price_includes_iva), rx.text(rx.cond(AppState.edit_price_includes_iva, "Sí", "No")))),
                        rx.vstack(rx.text("Origen"), rx.hstack(rx.switch(name="is_imported", is_checked=AppState.edit_is_imported, on_change=AppState.set_edit_is_imported), rx.text(rx.cond(AppState.edit_is_imported, "Importado", "Nacional")))),
                        columns="2", spacing="3", width="100%"
                    ),
                    rx.grid(
                        rx.vstack(rx.text("Costo de Envío Mínimo"), rx.input(name="edit_shipping_cost_str", value=AppState.edit_shipping_cost_str, on_change=AppState.set_edit_shipping_cost_str, size="3")),
                        rx.vstack(rx.text("Moda Completa"), rx.hstack(rx.switch(name="edit_is_moda_completa", is_checked=AppState.edit_is_moda_completa, on_change=AppState.set_edit_is_moda_completa), rx.text(rx.cond(AppState.edit_is_moda_completa, "Activo", "Inactivo")))),
                        rx.vstack(rx.text("Envío Combinado"), rx.hstack(rx.switch(name="combines_shipping", is_checked=AppState.edit_combines_shipping, on_change=AppState.set_edit_combines_shipping), rx.text(rx.cond(AppState.edit_combines_shipping, "Activo", "Inactivo")))),
                        rx.vstack(rx.text("Límite Combinado"), rx.input(name="edit_shipping_combination_limit_str", value=AppState.edit_shipping_combination_limit_str, on_change=AppState.set_edit_shipping_combination_limit_str, size="3", is_disabled=~AppState.edit_combines_shipping)),
                        columns="2", spacing="4", width="100%",
                    ),
                    rx.text("Descripción", as_="div", size="2", weight="bold"),
                    rx.text_area(name="content", value=AppState.edit_post_content, on_change=AppState.set_edit_post_content, required=True, size="2", style={"height": "120px"}),
                    spacing="3", align_items="stretch"
                ),
                columns={"initial": "1", "md": "2"}, spacing="6", width="100%",
            ),
            rx.divider(margin_y="1.5em"),
            rx.hstack(
                rx.alert_dialog.root(
                    rx.alert_dialog.trigger(rx.button("Eliminar Publicación", color_scheme="red", variant="soft", type="button")),
                    rx.alert_dialog.content(
                        rx.alert_dialog.title("Confirmar Eliminación"),
                        rx.alert_dialog.description("¿Estás absolutamente seguro? Esta acción no se puede deshacer y eliminará el producto permanentemente."),
                        rx.flex(
                            rx.alert_dialog.cancel(rx.button("Cancelar", variant="soft", color_scheme="gray")),
                            rx.alert_dialog.action(rx.button("Sí, Eliminar Permanentemente", on_click=AppState.delete_post(AppState.post_to_edit_id), color_scheme="red")),
                            spacing="3", margin_top="1em", justify="end",
                        ),
                    ),
                ),
                rx.spacer(),
                rx.button("Guardar Cambios", type="submit", size="3", color_scheme="violet"),
                justify="between",
                align="center",
                width="100%",
            ),
        ),
        on_submit=AppState.save_edited_post,
        width="100%",
    )