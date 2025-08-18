# likemodas/blog/forms.py

import reflex as rx
from ..state import AppState
from ..models import Category
from ..ui.components import multi_select_component, searchable_select
# Se importan las listas nuevas y actualizadas
from ..data.product_options import (
    LISTA_COLORES, LISTA_TALLAS_ROPA, LISTA_MATERIALES, 
    LISTA_NUMEROS_CALZADO, LISTA_TAMANOS_MOCHILAS
)

def blog_post_add_form() -> rx.Component:
    """Formulario para añadir productos con características dinámicas y con buscador."""
    
    material_selector = searchable_select(
        placeholder=AppState.material_label + "...",
        options=AppState.filtered_attr_materiales,
        on_change_select=AppState.set_attr_material, 
        value_select=AppState.attr_material,
        search_value=AppState.search_attr_material, 
        on_change_search=AppState.set_search_attr_material,
        filter_name="attr_material_filter",
    )

    caracteristicas_ropa = rx.grid(
        searchable_select( # El selector de color no cambia
            placeholder="Color...", options=AppState.filtered_attr_colores,
            on_change_select=AppState.set_attr_color, value_select=AppState.attr_color,
            search_value=AppState.search_attr_color, on_change_search=AppState.set_search_attr_color,
            filter_name="attr_color_filter",
        ),
        
        # --- ✨ CORRECCIÓN AQUÍ ---
        multi_select_component(
            placeholder="Añadir talla...",
            options=AppState.filtered_attr_tallas_ropa,
            selected_items=AppState.attr_tallas_ropa,
            # Usamos los nuevos argumentos
            add_handler=AppState.add_attribute_value,
            remove_handler=AppState.remove_attribute_value,
            prop_name="attr_tallas_ropa",
            search_value=AppState.search_attr_talla_ropa,
            on_change_search=AppState.set_search_attr_talla_ropa,
            filter_name="attr_talla_filter",
        ),
        material_selector,
        columns="3", spacing="3", width="100%",
    )

    caracteristicas_calzado = rx.grid(
        searchable_select(placeholder="Color...", options=AppState.filtered_attr_colores, on_change_select=AppState.set_attr_color, value_select=AppState.attr_color, search_value=AppState.search_attr_color, on_change_search=AppState.set_search_attr_color, filter_name="attr_color_filter"),
        
        # --- ✨ CORRECCIÓN AQUÍ ---
        multi_select_component(
            placeholder="Añadir número...",
            options=AppState.filtered_attr_numeros_calzado,
            selected_items=AppState.attr_numeros_calzado,
            # Usamos los nuevos argumentos
            add_handler=AppState.add_attribute_value,
            remove_handler=AppState.remove_attribute_value,
            prop_name="attr_numeros_calzado",
            search_value=AppState.search_attr_numero_calzado,
            on_change_search=AppState.set_search_attr_numero_calzado,
            filter_name="attr_numero_filter",
        ),
        material_selector,
        columns="3", spacing="3", width="100%",
    )

    caracteristicas_mochilas = rx.grid(
        searchable_select(placeholder="Color...", options=AppState.filtered_attr_colores, on_change_select=AppState.set_attr_color, value_select=AppState.attr_color, search_value=AppState.search_attr_color, on_change_search=AppState.set_search_attr_color, filter_name="attr_color_filter"),

        # --- ✨ CORRECCIÓN AQUÍ ---
        multi_select_component(
            placeholder="Añadir tamaño...",
            options=AppState.filtered_attr_tamanos_mochila,
            selected_items=AppState.attr_tamanos_mochila,
            # Usamos los nuevos argumentos
            add_handler=AppState.add_attribute_value,
            remove_handler=AppState.remove_attribute_value,
            prop_name="attr_tamanos_mochila",
            search_value=AppState.search_attr_tamano_mochila,
            on_change_search=AppState.set_search_attr_tamano_mochila,
            filter_name="attr_tamano_mochila_filter",
        ),
        material_selector,
        columns="3", spacing="3", width="100%",
    )

    # El resto de la función (el return rx.form(...)) no necesita cambios.
    # Simplemente asegúrate de que use las variables de características corregidas de arriba.
    return rx.form(
        rx.vstack(
            rx.heading("Añadir Nuevo Producto", size="8", margin_bottom="1.5em"),
            rx.grid(
                # Columna Izquierda (Imágenes)
                rx.vstack(
                    rx.text("Imágenes del Producto", as_="div", size="2", weight="bold", margin_bottom="0.5em"),
                    rx.upload(
                        rx.vstack(rx.icon("upload", size=32), rx.text("Subir imágenes (máx 5)")),
                        id="blog_upload", multiple=True, max_files=5,
                        on_drop=AppState.handle_add_upload(rx.upload_files("blog_upload")),
                        border="2px dashed #ccc", padding="2em", width="100%"
                    ),
                    rx.cond(
                        AppState.temp_images,
                        rx.grid(
                            rx.foreach(
                                AppState.temp_images,
                                lambda img: rx.box(
                                    rx.image(src=rx.get_upload_url(img), width="100px", height="100px", object_fit="cover"),
                                    rx.icon_button(rx.icon("trash-2"),
                                        on_click=AppState.remove_temp_image(img),
                                        size="1", color_scheme="red", variant="soft",
                                        style={"position": "absolute", "top": "4px", "right": "4px"}
                                    ),
                                    position="relative"
                                ),
                            ),
                            columns="4", spacing="2", margin_top="1em"
                        )
                    ),
                    spacing="2",
                ),
                # Columna Derecha (Datos del producto)
                rx.vstack(
                    rx.text("Título del Producto", as_="div", size="2", weight="bold"),
                    rx.input(placeholder="Nombre del producto", name="title", required=True, size="3"),

                    rx.text("Categoría", as_="div", size="2", weight="bold"),
                    rx.select(
                        AppState.categories,
                        placeholder="Selecciona una categoría...", name="category",
                        required=True, size="3", on_change=AppState.set_category,
                    ),

                    rx.text("Precio (COP)", as_="div", size="2", weight="bold"),
                    rx.input(placeholder="Ej: 55000 (sin puntos)", type="number", name="price", required=True, size="3"),

                    rx.cond(
                        AppState.category != "",
                        rx.vstack(
                            rx.text("Características del Producto", as_="div", size="2", weight="bold"),
                            rx.cond(AppState.category == Category.ROPA.value, caracteristicas_ropa),
                            rx.cond(AppState.category == Category.CALZADO.value, caracteristicas_calzado),
                            rx.cond(AppState.category == Category.MOCHILAS.value, caracteristicas_mochilas),
                            align_items="stretch", width="100%",
                        )
                    ),

                    rx.text("Descripción", as_="div", size="2", weight="bold"),
                    rx.text_area(
                        placeholder="Detalles del producto...", name="content",
                        required=True, size="2", style={"height": "150px"},
                    ),
                    rx.hstack(
                        rx.button("Publicar Ahora", type="submit", color_scheme="green", size="3"),
                        width="100%", 
                        justify="end",
                    ),
                    spacing="3",
                    align_items="stretch",
                    width="100%",
                ),
                columns="2",
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

def blog_post_edit_form() -> rx.Component:
    """El formulario para editar una publicación."""
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

            # ✨ Contenedor para el Título
            rx.vstack(
                rx.text("Título del Producto", as_="div", size="2", margin_top="1em", weight="bold"),
                rx.input(name="title", value=AppState.post_title, on_change=AppState.set_post_title, required=True, width="100%", style={"text_align": "center"}),
                width="100%"
            ),

            # ✨ Contenedor para la Descripción
            rx.vstack(
                rx.text("Descripción", as_="div", size="2", margin_bottom="2px", weight="bold"),
                rx.text_area(name="content", value=AppState.post_content, on_change=AppState.set_post_content, rows="8", required=True, width="100%", style={"text-align": "center"}),
                width="100%"
            ),

            # ✨ Contenedor para el Precio
            rx.vstack(
                rx.text("Precio (COP)", as_="div", size="2", margin_bottom="2px", weight="bold"),
                rx.input(name="price", value=AppState.price_str, on_change=AppState.set_price, type="number", required=True, width="100%", style={"text-align": "center"}),
                width="100%"
            ),

            rx.button("Guardar Cambios", type="submit", width="100%", margin_top="1em", size="3"),
            spacing="4", width="100%"
        ),
        on_submit=AppState.save_edited_post,
        width="100%",
    )