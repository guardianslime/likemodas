import reflex as rx
from ..state import AppState
from ..models import Category
from ..ui.components import multi_select_component, searchable_select
from ..data.product_options import (
    LISTA_COLORES, LISTA_TALLAS_ROPA, LISTA_MATERIALES, 
    LISTA_NUMEROS_CALZADO, LISTA_TAMANOS_MOCHILAS
)

def variant_stock_manager() -> rx.Component:
    """Componente para gestionar el stock de las variantes generadas."""
    return rx.vstack(
        rx.heading("Gestión de Variantes y Stock", size="4", margin_top="1em"),
        rx.text("Genera combinaciones y asigna un stock inicial a cada una.", size="2", color_scheme="gray"),
        
        rx.button("Generar / Actualizar Variantes", on_click=AppState.generate_variants, margin_y="1em"),
        
        # --- CAMBIO CLAVE EN LA UI ---
        # La tabla ahora depende de `current_generated_variants`, que está
        # ligado a la imagen seleccionada (`selected_variant_index`).
        rx.cond(
            AppState.current_generated_variants,
            rx.vstack(
                rx.foreach(
                    AppState.current_generated_variants,
                    lambda variant, index: rx.box(
                        rx.hstack(
                            # Atributos de la variante
                            rx.vstack(
                                rx.foreach(
                                    variant.attributes.items(),
                                    lambda item: rx.text(f"{item[0]}: ", rx.text.strong(item[1])),
                                ),
                                align_items="start", flex_grow=1,
                            ),
                            
                            # Contador de stock (ahora pasa el índice del grupo y del item)
                            rx.hstack(
                                rx.icon_button(rx.icon("minus"), on_click=AppState.decrement_variant_stock(AppState.selected_variant_index, index)),
                                rx.input(
                                    value=variant.stock.to_string(),
                                    on_change=lambda val: AppState.set_variant_stock(AppState.selected_variant_index, index, val),
                                    text_align="center", max_width="70px",
                                ),
                                rx.icon_button(rx.icon("plus"), on_click=AppState.increment_variant_stock(AppState.selected_variant_index, index)),
                                align="center", spacing="2",
                            ),
                            
                            # Selector de imagen (ahora pasa el índice del grupo y del item)
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
    color_selector_multiple = multi_select_component(
        placeholder="Añadir color...", options=AppState.filtered_attr_colores,
        selected_items=AppState.attr_colores, add_handler=AppState.add_attribute_value,
        remove_handler=AppState.remove_attribute_value, prop_name="attr_colores",
        search_value=AppState.search_attr_color, on_change_search=AppState.set_search_attr_color,
        filter_name="attr_color_filter",
    )
    caracteristicas_ropa = rx.vstack(
        rx.grid(
            color_selector_multiple,
            multi_select_component(
                placeholder="Añadir talla...", options=AppState.filtered_attr_tallas_ropa,
                selected_items=AppState.attr_tallas_ropa, add_handler=AppState.add_attribute_value,
                remove_handler=AppState.remove_attribute_value, prop_name="attr_tallas_ropa",
                search_value=AppState.search_attr_talla_ropa, on_change_search=AppState.set_search_attr_talla_ropa,
                filter_name="attr_talla_filter",
            ),
            columns="2", spacing="3", width="100%",
        ),
        rx.grid(tipo_selector, material_selector, columns="2", spacing="3", width="100%"),
        spacing="3", width="100%",
    )
    caracteristicas_calzado = rx.vstack(
        rx.grid(
            color_selector_multiple,
            multi_select_component(
                placeholder="Añadir número...", options=AppState.filtered_attr_numeros_calzado,
                selected_items=AppState.attr_numeros_calzado, add_handler=AppState.add_attribute_value,
                remove_handler=AppState.remove_attribute_value, prop_name="attr_numeros_calzado",
                search_value=AppState.search_attr_numero_calzado, on_change_search=AppState.set_search_attr_numero_calzado,
                filter_name="attr_numero_filter",
            ),
            columns="2", spacing="3", width="100%",
        ),
        rx.grid(tipo_selector, material_selector, columns="2", spacing="3", width="100%"),
        spacing="3", width="100%",
    )
    caracteristicas_mochilas = rx.vstack(
        rx.grid(
            color_selector_multiple,
            multi_select_component(
                placeholder="Añadir tamaño...", options=AppState.filtered_attr_tamanos_mochila,
                selected_items=AppState.attr_tamanos_mochila, add_handler=AppState.add_attribute_value,
                remove_handler=AppState.remove_attribute_value, prop_name="attr_tamanos_mochila",
                search_value=AppState.search_attr_tamano_mochila, on_change_search=AppState.set_search_attr_tamano_mochila,
                filter_name="attr_tamano_mochila_filter",
            ),
            columns="2", spacing="3", width="100%",
        ),
        rx.grid(tipo_selector, material_selector, columns="2", spacing="3", width="100%"),
        spacing="3", width="100%",
    )
    
    return rx.form(
        rx.vstack(
            rx.heading("Añadir Nuevo Producto", size="8", margin_bottom="1.5em"),
            rx.grid(
                rx.vstack(
                    rx.text("Imágenes del Producto", as_="div", size="2", weight="bold", margin_bottom="0.5em"),
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
                                        border_width=rx.cond(AppState.selected_variant_index == index, "3px", "1px"),
                                        border_color=rx.cond(AppState.selected_variant_index == index, "violet", "gray"),
                                        padding="2px", border_radius="lg", cursor="pointer",
                                        on_click=AppState.select_variant_for_editing(index),
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
                    rx.text("Título del Producto", as_="div", size="2", weight="bold"),
                    rx.input(placeholder="Nombre del producto", name="title", required=True, size="3"),
                    rx.text("Categoría", as_="div", size="2", weight="bold"),
                    rx.select(
                        AppState.categories, placeholder="Selecciona una categoría...", name="category",
                        required=True, size="3", on_change=AppState.set_category,
                    ),
                    rx.grid(
                        rx.vstack(
                            rx.text("Precio (COP)", as_="div", size="2", weight="bold"),
                            rx.input(placeholder="Ej: 55000 (sin puntos)", type="number", name="price", required=True, size="3"),
                        ),
                        rx.vstack(
                            rx.text("Incluye IVA (19%)", as_="div", size="2", weight="bold"),
                            rx.hstack(
                                rx.switch(is_checked=AppState.price_includes_iva, on_change=AppState.set_price_includes_iva, size="2"),
                                rx.text(rx.cond(AppState.price_includes_iva, "Sí", "No")),
                                align="center", spacing="3", height="100%",
                            ),
                        ),
                        rx.vstack(
                            rx.text("Origen", as_="div", size="2", weight="bold"),
                            rx.hstack(
                                rx.switch(is_checked=AppState.is_imported, on_change=AppState.set_is_imported, size="2"),
                                rx.text(rx.cond(AppState.is_imported, "Importado", "Nacional")),
                                align="center", spacing="3", height="100%",
                            ),
                        ),
                        columns="3", spacing="4", width="100%",
                    ),
                    rx.grid(
                        rx.vstack(
                            rx.text("Costo de Envío Mínimo (Local)", as_="div", size="2", weight="bold"),
                            rx.input(placeholder="Ej: 3000. Para envíos en tu mismo barrio.", type="number", value=AppState.shipping_cost_str, on_change=AppState.set_shipping_cost_str, size="3"),
                            rx.text("El costo final aumentará según la distancia.", size="1", color_scheme="gray"),
                            align_items="stretch",
                        ),
                        rx.vstack(
                            rx.text("Moda Completa", as_="div", size="2", weight="bold"),
                            rx.hstack(
                                rx.switch(is_checked=AppState.is_moda_completa, on_change=AppState.set_is_moda_completa, size="2"),
                                rx.text("Activo"),
                                align="center", spacing="3", height="100%",
                            ),
                            rx.text("Aplica para envío gratis en compras > $200.000.", size="1", color_scheme="gray"),
                            align_items="stretch",
                        ),
                        rx.vstack(
                            rx.text("Envío Combinado", as_="div", size="2", weight="bold"),
                            rx.hstack(
                                rx.switch(is_checked=AppState.combines_shipping, on_change=AppState.set_combines_shipping, size="2"),
                                rx.text("Activo"),
                                align="center", spacing="3", height="100%",
                            ),
                            rx.text("Permite que varios productos usen un solo envío.", size="1", color_scheme="gray"),
                            align_items="stretch",
                        ),
                        rx.vstack(
                            rx.text("Límite de Productos", as_="div", size="2", weight="bold"),
                            rx.input(
                                placeholder="Ej: 3", type="number",
                                value=AppState.shipping_combination_limit_str,
                                on_change=AppState.set_shipping_combination_limit_str,
                                size="3", is_disabled=~AppState.combines_shipping,
                            ),
                            rx.text("Máx. de items por cada cobro de envío.", size="1", color_scheme="gray"),
                            align_items="stretch",
                        ),
                        columns="2", spacing="4", width="100%",
                    ),
                    
                    # --- ✨ INICIO DE LA CORRECCIÓN ✨ ---
                    # La condición ahora solo depende de que se haya seleccionado una categoría
                    rx.cond(
                        AppState.category != "",
                        rx.vstack(
                            rx.text("Características del Producto", as_="div", size="2", weight="bold"),
                            rx.cond(AppState.category == Category.ROPA.value, caracteristicas_ropa),
                            rx.cond(AppState.category == Category.CALZADO.value, caracteristicas_calzado),
                            rx.cond(AppState.category == Category.MOCHILAS.value, caracteristicas_mochilas),
                            
                            # AÑADE EL NUEVO COMPONENTE AQUÍ
                            variant_stock_manager(),
                            
                            align_items="stretch", width="100%",
                        )
                    ),
                    # --- ✨ FIN DE LA CORRECCIÓN ✨ ---

                    rx.text("Descripción", as_="div", size="2", weight="bold"),
                    rx.text_area(placeholder="Detalles del producto...", name="content", required=True, size="2", style={"height": "150px"}),
                    rx.hstack(
                        rx.button("Publicar Ahora", type="submit", color_scheme="green", size="3"),
                        width="100%", justify="end",
                    ),
                    spacing="3", align_items="stretch", width="100%",
                ),
                columns="2", spacing="6", width="100%", align_items="start",
            ),
            spacing="5", max_width="1024px",
        ),
        on_submit=AppState.submit_and_publish,
        reset_on_submit=True,
        width="100%", max_width="1024px",
    )

def blog_post_edit_form() -> rx.Component:
    """El formulario para editar una publicación."""
    # (Este formulario no necesita cambios)
    return rx.form(
        rx.vstack(
            rx.text("Imágenes del Producto", as_="div", size="2", weight="bold"),
            rx.grid(
                rx.foreach(
                    AppState.post_images_in_form,
                    lambda img_url: rx.box(
                        rx.image(src=rx.get_upload_url(img_url), width="100px", height="100px", object_fit="cover", border_radius="md"),
                        rx.icon_button(
                            rx.icon("trash-2", size=16),
                            on_click=AppState.remove_edited_image(img_url),
                            color_scheme="red", variant="soft", size="1",
                            style={"position": "absolute", "top": "4px", "right": "4px"}
                        ),
                        position="relative",
                    )
                ),
                columns="4", spacing="2", width="100%", margin_bottom="1em"
            ),
            rx.upload(
                rx.vstack(rx.icon("upload", size=24), rx.text("Añadir nuevas imágenes", size="2")),
                id="edit_upload", multiple=True, max_files=5,
                on_drop=AppState.handle_edit_upload(rx.upload_files("edit_upload")),
                border="2px dashed #ccc", padding="1em", width="100%"
            ),
            rx.vstack(
                rx.text("Título del Producto", as_="div", size="2", margin_top="1em", weight="bold"),
                rx.input(name="title", value=AppState.post_title, on_change=AppState.set_post_title, required=True, width="100%", style={"text_align": "center"}),
                width="100%"
            ),
            rx.vstack(
                rx.text("Descripción", as_="div", size="2", margin_bottom="2px", weight="bold"),
                rx.text_area(name="content", value=AppState.post_content, on_change=AppState.set_post_content, rows="8", required=True, width="100%", style={"text_align": "center"}),
                width="100%"
            ),
            rx.vstack(
                rx.text("Precio (COP)", as_="div", size="2", margin_bottom="2px", weight="bold"),
                rx.input(name="price", value=AppState.price_str, on_change=AppState.set_price, type="number", required=True, width="100%", style={"text_align": "center"}),
                width="100%"
            ),
            rx.button("Guardar Cambios", type="submit", width="100%", margin_top="1em", size="3"),
            spacing="4", width="100%"
        ),
        on_submit=AppState.save_edited_post,
        width="100%",
    )