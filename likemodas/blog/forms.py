# likemodas/blog/forms.py 

import reflex as rx

from likemodas.blog.state import BlogAdminState
from ..state import AppState, VariantGroupDTO
from ..models import Category
from ..ui.components import searchable_select
from ..data.product_options import (
    LISTA_COLORES, LISTA_TALLAS_ROPA, LISTA_NUMEROS_CALZADO,
    LISTA_TAMANOS_MOCHILAS
)

def image_selection_grid() -> rx.Component:
    """Muestra las imágenes subidas que aún no han sido agrupadas."""
    return rx.vstack(
        rx.text("Imágenes Disponibles", as_="div", size="3", weight="bold", margin_bottom="0.5em"),
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
                            rx.image(src=rx.get_upload_url(img_name), width="80px", height="80px", object_fit="cover", border_radius="md"),
                            rx.cond(
                                AppState.image_selection_for_grouping.contains(img_name),
                                rx.box(
                                    rx.icon("check", color="white", size=24),
                                    bg="rgba(90, 40, 180, 0.7)",
                                    position="absolute", inset="0", border_radius="md",
                                    display="flex", align_items="center", justify_content="center"
                                )
                            ),
                            border="2px solid",
                            border_color=rx.cond(AppState.image_selection_for_grouping.contains(img_name), "var(--violet-9)", "transparent"),
                            border_radius="lg", cursor="pointer", position="relative",
                            on_click=AppState.toggle_image_selection_for_grouping(img_name),
                        )
                    ),
                    wrap="wrap", spacing="3", padding_top="1em",
                ),
                rx.button("Crear Grupo con Imágenes Seleccionadas", on_click=AppState.create_variant_group, margin_top="1em"),
                align_items="start",
            )
        ),
        spacing="3", width="100%", align_items="stretch",
    )

def variant_group_manager() -> rx.Component:
    """Muestra y permite la gestión de los grupos de variantes ya creados."""
    def render_group_card(group: VariantGroupDTO, index: rx.Var[int]) -> rx.Component:
        is_selected = AppState.selected_group_index == index
        group_attribute_editor = rx.vstack(
            rx.text("Color", size="2", weight="medium"),
            searchable_select(
                placeholder="Seleccionar color...", options=AppState.filtered_attr_colores,
                on_change_select=AppState.set_temp_color, value_select=AppState.temp_color,
                search_value=AppState.search_attr_color, on_change_search=AppState.set_search_attr_color,
                filter_name=f"color_filter_{index}",
            ),
            rx.text("Tallas", size="2", weight="medium"),
            rx.flex(
                rx.foreach(
                    AppState.attr_tallas_ropa,
                    lambda talla: rx.badge(
                        talla, rx.icon("x", size=12, on_click=AppState.remove_variant_attribute("Talla", talla), cursor="pointer"),
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
                            rx.text(variant.attributes["Talla"]), rx.spacer(),
                            rx.icon_button(rx.icon("minus"), on_click=AppState.decrement_variant_stock(index, var_index), size="1"),
                            rx.input(value=variant.stock.to_string(), on_change=lambda val: AppState.set_variant_stock(index, var_index, val), text_align="center", max_width="50px"),
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
        rx.heading("Grupos de Variantes", size="4", margin_top="1em"),
        rx.text("Agrupa imágenes que representan una misma variante (ej. mismo color). Luego, asigna atributos y genera el stock para cada grupo.", size="2", color_scheme="gray"),
        rx.cond(
            AppState.variant_groups,
            rx.vstack(
                rx.foreach(AppState.variant_groups, render_group_card),
                spacing="4"
            ),
            rx.text("Aún no has creado ningún grupo.", color_scheme="gray", padding="1em 0")
        ),
        align_items="stretch", spacing="3", width="100%",
    )

# --- ✨ FORMULARIO PRINCIPAL RESTAURADO CON LA LÓGICA NUEVA ✨ ---
def blog_post_add_form() -> rx.Component:
    """Formulario para añadir productos, restaurado al diseño original de 2 columnas."""
    return rx.form(
        rx.vstack(
            rx.grid(
                # --- COLUMNA IZQUIERDA: IMÁGENES Y GRUPOS ---
                rx.vstack(
                    image_selection_grid(),
                    rx.divider(margin_y="1.5em"),
                    variant_group_manager(),
                    spacing="4",
                ),
                # --- COLUMNA DERECHA: DATOS DEL PRODUCTO ---
                rx.vstack(
                    rx.vstack(
                        rx.text("Título del Producto"),
                        rx.input(name="title", on_change=AppState.set_title, required=True),
                        align_items="stretch",
                    ),
                    rx.vstack(
                        rx.text("Categoría"),
                        rx.select(AppState.categories, on_change=AppState.set_category, name="category", required=True),
                        align_items="stretch",
                    ),
                    rx.grid(
                        rx.vstack(rx.text("Precio (COP)"), rx.input(name="price", on_change=AppState.set_price, type="number", required=True)),
                        rx.vstack(rx.text("Ganancia (COP)"), rx.input(name="profit", value=AppState.profit_str, on_change=AppState.set_profit_str, type="number")),
                        columns="2", spacing="4"
                    ),
                    rx.vstack(
                        rx.text("Descripción"),
                        rx.text_area(name="content", on_change=AppState.set_content, style={"height": "120px"}),
                        align_items="stretch",
                    ),
                    # ... Aquí puedes volver a añadir las opciones de envío como las tenías antes si quieres ...
                    spacing="4", align_items="stretch",
                ),
                columns={"initial": "1", "md": "2"}, 
                spacing="6", 
                width="100%", 
                align_items="start",
            ),
            rx.divider(margin_y="2em"),
            rx.hstack(
                rx.button("Publicar Producto", type="submit", color_scheme="violet", size="3"),
                width="100%", justify="end",
            ),
            spacing="5", 
            max_width="1200px",
        ),
        on_submit=AppState.submit_and_publish,
        reset_on_submit=True,
        width="100%", 
    )

# --- Componente reutilizable para editar atributos (Sin cambios) ---
def attribute_editor(
    title: str,
    options_list: list[str],
    temp_value_var: rx.Var[str],
    temp_value_setter: rx.event.EventSpec,
    add_handler: rx.event.EventHandler,
    remove_handler: rx.event.EventHandler,
    current_selections: rx.Var[list[str]],
) -> rx.Component:
    """Un componente para añadir y quitar atributos específicos a una variante."""
    return rx.vstack(
        rx.text(title, weight="bold", size="3"),
        rx.flex(
            rx.foreach(
                current_selections,
                lambda item: rx.badge(
                    item,
                    rx.icon(
                        "x", size=12, cursor="pointer",
                        on_click=lambda: remove_handler(item),
                        margin_left="0.25em"
                    ),
                    variant="soft", color_scheme="gray", size="2",
                ),
            ),
            wrap="wrap", spacing="2", min_height="36px",
        ),
        rx.hstack(
            rx.select(
                options_list,
                placeholder=f"Seleccionar {title.lower()}...",
                value=temp_value_var,
                on_change=temp_value_setter,
            ),
            rx.button("Añadir", on_click=add_handler, type="button", color_scheme="violet", variant="soft"),
            width="100%"
        ),
        align_items="stretch", width="100%", spacing="2"
    )

# --- Gestor de Stock para el formulario de AÑADIR (Sin cambios) ---
def variant_stock_manager() -> rx.Component:
    """Componente para gestionar el stock de las variantes generadas en el form de AÑADIR."""
    return rx.vstack(
        rx.heading("Gestión de Variantes y Stock", size="4", margin_top="1em"),
        rx.text("Genera combinaciones y asigna un stock inicial a cada una.", size="2", color_scheme="gray"),
        rx.button("Generar / Actualizar Variantes", on_click=AppState.generate_variants, margin_y="1em", type="button", color_scheme="violet"),
        rx.cond(
            (AppState.selected_variant_index >= 0) & AppState.generated_variants_map.contains(AppState.selected_variant_index),
            rx.vstack(
                rx.foreach(
                    AppState.generated_variants_map.get(AppState.selected_variant_index, []),
                    lambda variant, index: rx.box(
                        rx.hstack(
                            rx.vstack(
                                rx.foreach(
                                    variant.attributes.items(),
                                    lambda item: rx.text(f"{item[0]}: ", rx.text.strong(item[1])),
                                ),
                                align_items="start", flex_grow=1,
                            ),
                            rx.hstack(
                                rx.icon_button(rx.icon("minus"), on_click=AppState.decrement_variant_stock(AppState.selected_variant_index, index), type="button"),
                                rx.input(
                                    value=variant.stock.to_string(),
                                    on_change=lambda val: AppState.set_variant_stock(AppState.selected_variant_index, index, val),
                                    text_align="center", max_width="70px",
                                ),
                                rx.icon_button(rx.icon("plus"), on_click=AppState.increment_variant_stock(AppState.selected_variant_index, index), type="button"),
                                align="center", spacing="2",
                            ),
                            rx.select(
                                AppState.uploaded_image_urls,
                                placeholder="Imagen...",
                                value=variant.image_url,
                                on_change=lambda url: AppState.assign_image_to_variant(AppState.selected_variant_index, index, url),
                                max_width="150px",
                            ),
                            spacing="4", align="center", width="100%",
                        ),
                        padding="0.75em", border="1px solid",
                        border_color=rx.color("gray", 6), border_radius="md", width="100%",
                    )
                ),
                spacing="3", width="100%",
            )
        ),
        align_items="stretch", width="100%",
    )

# --- Gestor de Stock para el formulario de EDICIÓN (Sin cambios) ---
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
                                rx.foreach(
                                    variant.attributes.items(),
                                    lambda item: rx.text(f"{item[0]}: ", rx.text.strong(item[1])),
                                ),
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
                        padding="0.75em", border="1px solid",
                        border_color=rx.color("gray", 6), border_radius="md", width="100%",
                    )
                ),
                spacing="3", width="100%",
            )
        ),
        align_items="stretch", width="100%",
    )

def blog_post_add_form() -> rx.Component:
    """Formulario para añadir productos con características dinámicas y con buscador."""
    tipo_selector = searchable_select(
        placeholder="Tipo...", options=AppState.filtered_attr_tipos,
        on_change_select=AppState.set_attr_tipo, value_select=AppState.attr_tipo,
        search_value=AppState.search_attr_tipo, on_change_search=AppState.set_search_attr_tipo,
        filter_name="attr_tipo_filter",
    )
    material_selector = searchable_select(
        placeholder=AppState.material_label + "...", options=AppState.filtered_attr_materiales,
        on_change_select=AppState.set_attr_material, value_select=AppState.attr_material,
        search_value=AppState.search_attr_material, on_change_search=AppState.set_search_attr_material,
        filter_name="attr_material_filter",
    )
    color_selector_simple = searchable_select(
        placeholder="Selecciona un color...",
        options=AppState.filtered_attr_colores,
        on_change_select=AppState.set_attr_colores,
        value_select=AppState.attr_colores,
        search_value=AppState.search_attr_color,
        on_change_search=AppState.set_search_attr_color,
        filter_name="attr_color_filter",
    )

    caracteristicas_ropa = rx.vstack(
        rx.grid(
            color_selector_simple,
            attribute_editor(
                title="Talla", options_list=LISTA_TALLAS_ROPA,
                temp_value_var=AppState.temp_talla,
                temp_value_setter=AppState.set_temp_talla,
                add_handler=lambda: AppState.add_variant_attribute("Talla", AppState.temp_talla),
                remove_handler=lambda val: AppState.remove_variant_attribute("Talla", val),
                current_selections=AppState.attr_tallas_ropa,
            ),
            columns="2", spacing="3", width="100%",
        ),
        rx.grid(tipo_selector, material_selector, columns="2", spacing="3", width="100%"),
        spacing="3", width="100%",
    )
    caracteristicas_calzado = rx.vstack(
        rx.grid(
            color_selector_simple,
            attribute_editor(
                title="Número", options_list=LISTA_NUMEROS_CALZADO,
                temp_value_var=AppState.temp_numero,
                temp_value_setter=AppState.set_temp_numero,
                add_handler=lambda: AppState.add_variant_attribute("Número", AppState.temp_numero),
                remove_handler=lambda val: AppState.remove_variant_attribute("Número", val),
                current_selections=AppState.attr_numeros_calzado,
            ),
            columns="2", spacing="3", width="100%",
        ),
        rx.grid(tipo_selector, material_selector, columns="2", spacing="3", width="100%"),
        spacing="3", width="100%",
    )
    caracteristicas_mochilas = rx.vstack(
        rx.grid(
            color_selector_simple,
            attribute_editor(
                title="Tamaño", options_list=LISTA_TAMANOS_MOCHILAS,
                temp_value_var=AppState.temp_tamano,
                temp_value_setter=AppState.set_temp_tamano,
                add_handler=lambda: AppState.add_variant_attribute("Tamaño", AppState.temp_tamano),
                remove_handler=lambda val: AppState.remove_variant_attribute("Tamaño", val),
                current_selections=AppState.attr_tamanos_mochila,
            ),
            columns="2", spacing="3", width="100%",
        ),
        rx.grid(tipo_selector, material_selector, columns="2", spacing="3", width="100%"),
        spacing="3", width="100%",
    )

    return rx.form(
        rx.vstack(
            rx.grid(
                rx.vstack(
                    rx.text("Imágenes del Producto", as_="div", size="3", weight="bold", margin_bottom="0.5em"),
                    rx.upload(
                        rx.vstack(rx.icon("upload", size=32), rx.text("Subir imágenes (máx 5)")),
                        id="blog_upload", multiple=True, max_files=5,
                        on_drop=AppState.handle_add_upload(rx.upload_files("blog_upload")),
                        border="2px dashed #ccc", padding="2em", width="100%"
                    ),
                    rx.cond(
                        AppState.new_variants,
                        rx.vstack(
                            rx.text("Selecciona una imagen para añadirle características:", size="2", margin_top="1em"),
                            rx.flex(
                                rx.foreach(
                                    AppState.new_variants,
                                    lambda variant, index: rx.box(
                                        rx.image(src=rx.get_upload_url(variant.get("image_url", "")), width="80px", height="80px", object_fit="cover", border_radius="md"),
                                        rx.icon_button(
                                            rx.icon("trash-2", size=12),
                                            on_click=AppState.remove_add_image(index),
                                            color_scheme="red", variant="soft", size="1",
                                            style={"position": "absolute", "top": "2px", "right": "2px", "cursor": "pointer", "z_index": "10"}
                                        ),
                                        border_width=rx.cond(AppState.selected_variant_index == index, "3px", "1px"),
                                        border_color=rx.cond(AppState.selected_variant_index == index, "violet", "gray"),
                                        padding="2px", border_radius="lg", cursor="pointer",
                                        on_click=AppState.select_variant_for_editing(index),
                                        position="relative",
                                    )
                                ),
                                wrap="wrap", spacing="3", margin_top="0.5em"
                            ),
                            align_items="stretch"
                        )
                    ),
                    spacing="2",
                ),
                rx.vstack(
                    rx.form.field(
                        rx.vstack(
                            rx.form.label("Título del Producto", size="3"),
                            rx.input(
                                # ✨ CORRECCIÓN AQUÍ ✨
                                value=AppState.title,
                                on_change=AppState.set_title,
                                placeholder="Nombre del producto", name="title", required=True, size="3", width="100%"
                            ),
                            align_items="stretch", width="100%",
                        ),
                        width="100%",
                    ),
                    rx.text("Categoría", as_="div", size="3", weight="bold"),
                    rx.select(
                        AppState.categories, placeholder="Selecciona una categoría...", name="category",
                        required=True, size="3", on_change=AppState.set_category,
                    ),
                    rx.grid(
                        rx.vstack(
                            rx.text("Precio (COP)", as_="div", size="3", weight="bold"),
                            # --- ✨ CORRECCIÓN AQUÍ ✨ ---
                            rx.input(
                                placeholder="Ej: 55000 (sin puntos)", type="number", name="price", required=True, size="3",
                                value=AppState.price,
                                on_change=AppState.set_price, # <-- Asegúrate de que llama a set_price
                            ),
                        ),
                        rx.vstack(
                            rx.text("Ganancia (COP)", as_="div", size="3", weight="bold"),
                            rx.input(
                                placeholder="Ej: 15000 (sin puntos)", type="number", size="3",
                                name="profit",
                                value=AppState.profit_str,
                                # Este se mantiene, ahora tiene la lógica de validación
                                on_change=AppState.set_profit_str,
                            ),
                        ),
                        columns="2", spacing="4", width="100%",
                    ),
                    rx.grid(
                        rx.vstack(
                            rx.text("Incluye IVA (19%)", as_="div", size="3", weight="bold"),
                            rx.hstack(
                                rx.switch(is_checked=AppState.price_includes_iva, on_change=AppState.set_price_includes_iva, size="3"),
                                # ✨ Este ya estaba correcto, pero lo confirmamos ✨
                                rx.text(rx.cond(AppState.price_includes_iva, "Sí", "No"), size="3"),
                                align="center", spacing="3", height="100%",
                            ),
                        ),
                        rx.vstack(
                            rx.text("Origen", as_="div", size="3", weight="bold"),
                            rx.hstack(
                                rx.switch(is_checked=AppState.is_imported, on_change=AppState.set_is_imported, size="3"),
                                rx.text(rx.cond(AppState.is_imported, "Importado", "Nacional"), size="3"),
                                align="center", spacing="3", height="100%",
                            ),
                        ),
                        columns="2", spacing="4", width="100%", margin_top="1em"
                    ),
                    rx.grid(
                        rx.vstack(
                            rx.text("Costo de Envío Mínimo (Local)", as_="div", size="3", weight="bold"),
                            rx.input(placeholder="Ej: 3000.", type="number", value=AppState.shipping_cost_str, on_change=AppState.set_shipping_cost_str, size="3"),
                            rx.text("El costo final aumentará según la distancia.", size="1", color_scheme="gray"),
                            align_items="stretch",
                        ),
                        rx.vstack(
                            rx.text("Moda Completa", as_="div", size="3", weight="bold"),
                            rx.hstack(
                                rx.switch(is_checked=AppState.is_moda_completa, on_change=AppState.set_is_moda_completa, size="3"),
                                # ✨ --- INICIO DE LA CORRECCIÓN 1 --- ✨
                                # Se reemplaza el texto estático por uno condicional.
                                rx.text(rx.cond(AppState.is_moda_completa, "Activo", "Inactivo"), size="3"),
                                # ✨ --- FIN DE LA CORRECCIÓN 1 --- ✨
                                align="center", spacing="3", height="100%",
                            ),
                            # ✨ --- INICIO: CAMPO DE TEXTO CONDICIONAL --- ✨
                            rx.cond(
                                AppState.is_moda_completa,
                                rx.input(
                                    placeholder="Umbral de envío gratis",
                                    value=AppState.free_shipping_threshold_str,
                                    on_change=AppState.set_free_shipping_threshold_str,
                                    type="number",
                                    margin_top="0.5em"
                                )
                            ),
                            # ✨ --- FIN --- ✨
                            rx.text("Envío gratis en compras > $XXX.XXX", size="1", color_scheme="gray"),
                            align_items="stretch",
                        ),
                        rx.vstack(
                            rx.text("Envío Combinado", as_="div", size="3", weight="bold"),
                            rx.hstack(
                                rx.switch(is_checked=AppState.combines_shipping, on_change=AppState.set_combines_shipping, size="3"),
                                # ✨ --- INICIO DE LA CORRECCIÓN 2 --- ✨
                                # Se reemplaza el texto estático por uno condicional.
                                rx.text(rx.cond(AppState.combines_shipping, "Activo", "Inactivo"), size="3"),
                                # ✨ --- FIN DE LA CORRECCIÓN 2 --- ✨
                                align="center", spacing="3", height="100%",
                            ),
                            rx.text("Permite que varios productos usen un solo envío.", size="1", color_scheme="gray"),
                            align_items="stretch",
                        ),
                        rx.vstack(
                            rx.text("Límite de Productos", as_="div", size="3", weight="bold"),
                            rx.input(
                                placeholder="Ej: 3", type="number",
                                value=AppState.shipping_combination_limit_str,
                                on_change=AppState.set_shipping_combination_limit_str,
                                size="3", is_disabled=~AppState.combines_shipping,
                            ),
                            rx.text("Máx. de items por envío.", size="1", color_scheme="gray"),
                            align_items="stretch",
                        ),
                        columns="2", spacing="4", width="100%",
                    ),
                    rx.cond(
                        AppState.category != "",
                        rx.vstack(
                            rx.text("Características del Producto", as_="div", size="3", weight="bold"),
                            rx.cond(AppState.category == Category.ROPA.value, caracteristicas_ropa),
                            rx.cond(AppState.category == Category.CALZADO.value, caracteristicas_calzado),
                            rx.cond(AppState.category == Category.MOCHILAS.value, caracteristicas_mochilas),
                            variant_stock_manager(),
                            align_items="stretch", width="100%",
                        )
                    ),
                    rx.form.field(
                        rx.vstack(
                             rx.form.label("Descripción", size="3"),
                            rx.text_area(
                                value=BlogAdminState.post_form_data["content"],
                                on_change=lambda val: BlogAdminState.set_post_form_field("content", val),
                                placeholder="Detalles del producto...", name="content", required=True, size="3",
                                style={"height": "150px"}, width="100%"
                            ),
                            align_items="stretch", width="100%",
                        ),
                        width="100%",
                    ),
                    rx.hstack(
                        rx.button("Publicar Ahora", type="submit", color_scheme="violet", size="3"),
                        width="100%", justify="end",
                    ),
                    spacing="3", align_items="stretch", width="100%",
                ),
                columns={"initial": "1", "md": "2"}, 
                spacing="6", 
                width="100%", 
                align_items="start",
            ),
            spacing="5", 
            max_width="1024px",
        ),
        on_submit=AppState.submit_and_publish,
        reset_on_submit=True,
        width="100%", 
        max_width="1024px",
    )


# --- Formulario para EDITAR un producto (CON BOTÓN DE ELIMINAR CORREGIDO) ---
def blog_post_edit_form() -> rx.Component:
    """El formulario para editar una publicación, ahora con estado centralizado y robusto."""
    caracteristicas_ropa_edit = attribute_editor(
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
                # --- COLUMNA IZQUIERDA: IMÁGENES Y VARIANTES ---
                rx.vstack(
                    rx.text("Imágenes del Producto", as_="div", size="2", weight="bold", margin_bottom="0.5em"),
                    rx.flex(
                        rx.foreach(
                            AppState.unique_edit_form_images,
                            lambda img_url, index: rx.box(
                                rx.image(src=rx.get_upload_url(img_url), width="80px", height="80px", object_fit="cover", border_radius="md"),
                                # --- CORRECCIÓN: Se asegura que el botón de eliminar sea visible ---
                                rx.icon_button(
                                    rx.icon("trash-2", size=14),
                                    on_click=AppState.remove_edit_image(img_url),
                                    color_scheme="red", 
                                    variant="soft", 
                                    size="1",
                                    style={
                                        "position": "absolute", 
                                        "top": "2px", 
                                        "right": "2px", 
                                        "cursor": "pointer",
                                        "z_index": "10"
                                    }
                                ),
                                border_width=rx.cond(AppState.edit_selected_image_index == index, "3px", "1px"),
                                border_color=rx.cond(AppState.edit_selected_image_index == index, "violet", "gray"),
                                padding="2px", border_radius="lg", cursor="pointer",
                                on_click=AppState.select_edit_image_for_editing(index),
                                position="relative", # <-- Crucial para que el botón se posicione correctamente
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
                                LISTA_COLORES, placeholder="Seleccionar color...",
                                name="color",
                                value=AppState.edit_attr_colores,
                                on_change=AppState.set_edit_attr_colores,
                            ),
                            rx.cond(AppState.edit_category == Category.ROPA.value, caracteristicas_ropa_edit),
                            rx.divider(margin_y="1em"),
                            variant_stock_manager_edit(),
                            spacing="2", align_items="stretch", width="100%"
                        )
                    ),
                    spacing="2", align_items="stretch",
                ),

                # --- COLUMNA DERECHA: DETALLES DEL PRODUCTO (Sin cambios) ---
                rx.vstack(
                    rx.text("Título del Producto", as_="div", size="2", weight="bold"),
                    rx.input(name="title", value=AppState.edit_post_title, on_change=AppState.set_edit_post_title, required=True, size="3"),
                    rx.text("Categoría", as_="div", size="2", weight="bold"),
                    rx.select(
                        AppState.categories, placeholder="Selecciona una categoría...",
                        name="category",
                        value=AppState.edit_category,
                        on_change=AppState.set_edit_category,
                        required=True, size="3",
                    ),
                    rx.grid(
                        rx.vstack(
                            rx.text("Precio (COP)", as_="div", size="2", weight="bold"),
                            rx.input(name="price", value=AppState.edit_price_str, on_change=AppState.set_edit_price_str, type="number", required=True, size="3"),
                        ),
                        rx.vstack(
                            rx.text("Ganancia (COP)", as_="div", size="2", weight="bold"),
                            rx.input(
                                name="profit", # <-- ✨ CORRECCIÓN CLAVE AÑADIDA AQUÍ
                                value=AppState.edit_profit_str, 
                                on_change=AppState.set_edit_profit_str, 
                                type="number", 
                                size="3"
                            ),
                        ),
                        columns="2", spacing="3", width="100%",
                    ),
                    rx.grid(
                        rx.vstack(
                            rx.text("Incluye IVA", as_="div", size="2", weight="bold"),
                            rx.hstack(
                                rx.switch(name="price_includes_iva", is_checked=AppState.edit_price_includes_iva, on_change=AppState.set_edit_price_includes_iva),
                                rx.text(rx.cond(AppState.edit_price_includes_iva, "Sí", "No")),
                                align="center", spacing="3", height="100%",
                            ),
                        ),
                        rx.vstack(
                            rx.text("Origen", as_="div", size="2", weight="bold"),
                            rx.hstack(
                                rx.switch(name="is_imported", is_checked=AppState.edit_is_imported, on_change=AppState.set_edit_is_imported),
                                rx.text(rx.cond(AppState.edit_is_imported, "Importado", "Nacional")),
                                align="center", spacing="3", height="100%",
                            ),
                        ),
                        columns="2", spacing="3", width="100%", margin_top="1em" # Añadimos margen superior
                    ),
                    rx.grid(
                        rx.vstack(
                            rx.text("Costo de Envío Mínimo", as_="div", size="2", weight="bold"),
                            rx.input(name="edit_shipping_cost_str", value=AppState.edit_shipping_cost_str, on_change=AppState.set_edit_shipping_cost_str, size="3"),
                            align_items="stretch",
                        ),
                        rx.vstack(
                            rx.text("Moda Completa", as_="div", size="2", weight="bold"),
                            rx.hstack(
                                rx.switch(
                                    name="edit_is_moda_completa",
                                    is_checked=AppState.edit_is_moda_completa,
                                    on_change=AppState.set_edit_is_moda_completa,
                                ),
                                rx.text(rx.cond(AppState.edit_is_moda_completa, "Activo", "Inactivo")),
                                align="center", spacing="3", height="100%",
                            ),
                            align_items="stretch",
                        ),
                        rx.vstack(
                            rx.text("Envío Combinado", as_="div", size="2", weight="bold"),
                            rx.hstack(
                                rx.switch(
                                    name="combines_shipping",
                                    is_checked=AppState.edit_combines_shipping,
                                    on_change=AppState.set_edit_combines_shipping,
                                ),
                                rx.text(rx.cond(AppState.edit_combines_shipping, "Activo", "Inactivo")),
                                align="center", spacing="3", height="100%",
                            ),
                            align_items="stretch",
                        ),
                        rx.vstack(
                            rx.text("Límite Combinado", as_="div", size="2", weight="bold"),
                            rx.input(
                                name="edit_shipping_combination_limit_str",
                                value=AppState.edit_shipping_combination_limit_str,
                                on_change=AppState.set_edit_shipping_combination_limit_str,
                                size="3", is_disabled=~AppState.edit_combines_shipping,
                            ),
                            align_items="stretch",
                        ),
                        columns="2", spacing="4", width="100%",
                    ),
                    rx.text("Descripción", as_="div", size="2", weight="bold"),
                    rx.text_area(name="content", value=AppState.edit_post_content, on_change=AppState.set_edit_post_content, required=True, size="2", style={"height": "120px"}),
                    spacing="3", align_items="stretch"
                ),
                columns={"initial": "1", "md": "2"}, spacing="6", width="100%",
            ),
            
            # --- SECCIÓN DE BOTONES MODIFICADA ---
            rx.divider(margin_y="1.5em"),
            rx.hstack(
                # Botón de Eliminar con diálogo de confirmación
                rx.alert_dialog.root(
                    rx.alert_dialog.trigger(
                        rx.button("Eliminar Publicación", color_scheme="red", variant="soft", type="button")
                    ),
                    rx.alert_dialog.content(
                        rx.alert_dialog.title("Confirmar Eliminación"),
                        rx.alert_dialog.description(
                            "¿Estás absolutamente seguro? Esta acción no se puede deshacer y eliminará el producto permanentemente."
                        ),
                        rx.flex(
                            rx.alert_dialog.cancel(
                                rx.button("Cancelar", variant="soft", color_scheme="gray")
                            ),
                            rx.alert_dialog.action(
                                # Llama al evento de borrado existente
                                rx.button("Sí, Eliminar Permanentemente", on_click=AppState.delete_post(AppState.post_to_edit_id), color_scheme="red")
                            ),
                            spacing="3", margin_top="1em", justify="end",
                        ),
                    ),
                ),
                rx.spacer(),
                # Botón de Guardar Cambios
                rx.button("Guardar Cambios", type="submit", size="3", color_scheme="violet"),
                justify="between",
                align="center",
                width="100%",
            ),
        ),
        on_submit=AppState.save_edited_post,
        width="100%",
    )