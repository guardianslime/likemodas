import reflex as rx
from .state import BlogAddFormState, BlogEditFormState, BlogPostState, SessionState
from ..models import Category
from ..data.product_options import LISTA_TIPOS_ROPA, LISTA_TIPOS_ZAPATOS, LISTA_TIPOS_MOCHILAS
from ..ui.components import searchable_select

def blog_post_add_form() -> rx.Component:
    """El formulario rediseñado para añadir un nuevo producto, con layout y tamaño ajustados para coincidir con la captura de pantalla."""
    return rx.form(
        rx.vstack(
            rx.heading("Añadir Nuevo Producto", size="8", margin_bottom="1em", width="100%", text_align="start"),
            
            # --- Grid principal con proporciones y espaciado ajustados ---
            rx.grid(
                # --- Columna Izquierda: Carga de Imágenes ---
                rx.vstack(
                    rx.card(
                        rx.vstack(
                            rx.upload(
                                rx.vstack(
                                    rx.icon("upload", size=48),
                                    rx.text("Subir imágenes del producto", size="4", weight="medium"),
                                ),
                                id="blog_upload",
                                multiple=True,
                                max_files=5,
                                accept={"image/*": [".jpg", ".png", ".jpeg", ".webp"]},
                                on_drop=BlogAddFormState.handle_upload(rx.upload_files("blog_upload")),
                                border="2px dashed",
                                border_color=rx.color("gray", 10),
                                padding="3em",
                                width="100%",
                                height="100%",
                                style={"cursor": "pointer"},
                            ),
                            align="center",
                            justify="center",
                            width="100%",
                            height="100%",
                        ),
                        width="100%",
                        height="100%",
                        min_height="420px",
                    ),
                    rx.cond(
                        BlogAddFormState.temp_images,
                        rx.hstack(
                            rx.foreach(
                                BlogAddFormState.temp_images,
                                lambda img: rx.box(
                                    rx.image(src=rx.get_upload_url(img), width="80px", height="80px", object_fit="cover", border_radius="md"),
                                    rx.icon(tag="trash", on_click=BlogAddFormState.remove_image(img), color="red", style={"position": "absolute", "top": "5px", "right": "5px", "cursor": "pointer"}),
                                    style={"position": "relative"},
                                ),
                            ),
                            wrap="wrap",
                            spacing="3",
                            padding_top="1em",
                        )
                    ),
                    spacing="4",
                    width="100%",
                    height="100%",
                ),

                # --- Columna Derecha: Información y Características ---
                rx.vstack(
                    rx.input(placeholder="Nombre del producto", value=BlogAddFormState.title, on_change=BlogAddFormState.set_title, required=True, size="3"),
                    rx.hstack(
                        rx.input(placeholder="0", type="number", value=BlogAddFormState.price.to_string(), on_change=BlogAddFormState.set_price_from_input, required=True, size="3"),
                        rx.select(BlogPostState.categories, placeholder="ropa", value=BlogAddFormState.category, on_change=BlogAddFormState.set_category, required=True, size="3"),
                        spacing="4",
                        width="100%",
                    ),
                    rx.text_area(placeholder="Descripción del producto...", value=BlogAddFormState.content, on_change=BlogAddFormState.set_content, required=True, size="2", style={"height": "160px"}),
                    
                    # Sección de Características Adicionales
                    rx.vstack(
                        rx.hstack(
                           rx.text("Características Adicionales", weight="bold", size="5"),
                           rx.spacer(),
                           rx.button("Limpiar", on_click=BlogAddFormState.clear_all_attributes, size="1", variant="soft", color_scheme="gray"),
                           justify="between",
                           align_items="center",
                           width="100%",
                           margin_top="1em",
                           margin_bottom="0.5em",
                        ),
                        rx.cond(
                            BlogAddFormState.category == Category.ROPA.value,
                            rx.grid(
                                searchable_select(placeholder="Tipo de Prenda", options=SessionState.filtered_tipos_ropa, on_change_select=BlogAddFormState.set_tipo_prenda, value_select=BlogAddFormState.tipo_prenda, search_value=BlogAddFormState.search_add_tipo_prenda, on_change_search=BlogAddFormState.set_search_add_tipo_prenda, filter_name="add_form_tipo_prenda"),
                                searchable_select(placeholder="Color", options=BlogAddFormState.filtered_add_colores, on_change_select=BlogAddFormState.set_color_ropa, value_select=BlogAddFormState.color_ropa, search_value=BlogAddFormState.search_add_color_ropa, on_change_search=BlogAddFormState.set_search_add_color_ropa, filter_name="add_form_color_ropa"),
                                searchable_select(placeholder="Talla (S, M, L...)", options=BlogAddFormState.filtered_add_tallas, on_change_select=BlogAddFormState.set_talla, value_select=BlogAddFormState.talla, search_value=BlogAddFormState.search_add_talla, on_change_search=BlogAddFormState.set_search_add_talla, filter_name="add_form_talla"),
                                searchable_select(placeholder="Tipo de Tela", options=BlogAddFormState.filtered_add_materiales, on_change_select=BlogAddFormState.set_tipo_tela, value_select=BlogAddFormState.tipo_tela, search_value=BlogAddFormState.search_add_tipo_tela, on_change_search=BlogAddFormState.set_search_add_tipo_tela, filter_name="add_form_tipo_tela"),
                                columns="2", spacing="4", width="100%",
                            )
                        ),
                        rx.cond(
                            BlogAddFormState.category == Category.CALZADO.value,
                            rx.grid(
                                searchable_select(placeholder="Tipo de Zapato", options=SessionState.filtered_tipos_zapatos, on_change_select=BlogAddFormState.set_tipo_zapato, value_select=BlogAddFormState.tipo_zapato, search_value=BlogAddFormState.search_add_tipo_zapato, on_change_search=BlogAddFormState.set_search_add_tipo_zapato, filter_name="add_form_tipo_zapato"),
                                searchable_select(placeholder="Color", options=BlogAddFormState.filtered_add_colores, on_change_select=BlogAddFormState.set_color_calzado, value_select=BlogAddFormState.color_calzado, search_value=BlogAddFormState.search_add_color_calzado, on_change_search=BlogAddFormState.set_search_add_color_calzado, filter_name="add_form_color_calzado"),
                                searchable_select(placeholder="Número (38, 39...)", options=BlogAddFormState.filtered_add_numeros_calzado, on_change_select=BlogAddFormState.set_numero_calzado, value_select=BlogAddFormState.numero_calzado, search_value=BlogAddFormState.search_add_numero_calzado, on_change_search=BlogAddFormState.set_search_add_numero_calzado, filter_name="add_form_numero_calzado"),
                                searchable_select(placeholder="Material", options=BlogAddFormState.filtered_add_materiales, on_change_select=BlogAddFormState.set_material_calzado, value_select=BlogAddFormState.material_calzado, search_value=BlogAddFormState.search_add_material_calzado, on_change_search=BlogAddFormState.set_search_add_material_calzado, filter_name="add_form_material_calzado"),
                                columns="2", spacing="4", width="100%",
                            )
                        ),
                        rx.cond(
                            BlogAddFormState.category == Category.MOCHILAS.value,
                            rx.grid(
                                searchable_select(placeholder="Tipo de Mochila", options=SessionState.filtered_tipos_mochilas, on_change_select=BlogAddFormState.set_tipo_mochila, value_select=BlogAddFormState.tipo_mochila, search_value=BlogAddFormState.search_add_tipo_mochila, on_change_search=BlogAddFormState.set_search_add_tipo_mochila, filter_name="add_form_tipo_mochila"),
                                searchable_select(placeholder="Material", options=BlogAddFormState.filtered_add_materiales, on_change_select=BlogAddFormState.set_material_mochila, value_select=BlogAddFormState.material_mochila, search_value=BlogAddFormState.search_add_material_mochila, on_change_search=BlogAddFormState.set_search_add_material_mochila, filter_name="add_form_material_mochila"),
                                rx.input(placeholder="Medidas (e.g., 50x30cm)", value=BlogAddFormState.medidas, on_change=BlogAddFormState.set_medidas, size="2"),
                                columns="2", spacing="4", width="100%",
                            )
                        ),
                    ),
                    rx.spacer(),
                    align_items="stretch",
                    spacing="5",
                    width="100%",
                    height="100%",
                ),

                # Propiedades del Grid
                grid_template_columns={"base": "1fr", "lg": "1fr 1.2fr"},
                gap="2.5em",
                width="100%",
            ),

            # --- Botones de Acción ---
            rx.hstack(
                rx.button("Guardar Borrador", on_click=BlogAddFormState.submit, variant="soft", color_scheme="gray", size="3"),
                rx.button("Publicar Ahora", on_click=BlogAddFormState.submit_and_publish, color_scheme="green", size="3"),
                spacing="4",
                width="100%",
                justify="end",
                margin_top="1em",
            ),
            
            spacing="5",
            width="100%",
            max_width="1400px",
            padding="2em",
        ),
        on_submit=BlogAddFormState.submit_and_publish,
    )


def blog_post_edit_form() -> rx.Component:
    """El formulario para editar un post existente."""
    return rx.cond(
        BlogEditFormState.post,
        rx.form(
            rx.vstack(
                rx.input(
                    type="hidden",
                    name="post_id",
                    value=rx.cond(
                        BlogEditFormState.post.id,
                        BlogEditFormState.post.id,
                        ""
                    ),
                ),
                rx.input(
                    name="title",
                    value=rx.cond(
                        BlogEditFormState.post.title,
                        BlogEditFormState.post.title,
                        ""
                    ),
                    placeholder="Título del Post",
                    required=True,
                    width="100%",
                ),
                rx.input(
                    name="price",
                    value=BlogEditFormState.price_str,
                    on_change=BlogEditFormState.set_price,
                    placeholder="Precio",
                    required=True,
                    width="100%",
                ),
                rx.text_area(
                    name="content",
                    value=rx.cond(
                        BlogEditFormState.post_content != "",
                        BlogEditFormState.post_content,
                        ""
                    ),
                    on_change=BlogEditFormState.set_post_content,
                    placeholder="Escribe tu contenido aquí...",
                    required=True,
                    height="40vh",
                    width="100%",
                ),
                rx.flex(
                    rx.switch(
                        name="publish_active",
                        is_checked=BlogEditFormState.post_publish_active,
                        on_change=BlogEditFormState.set_post_publish_active,
                    ),
                    rx.text("Publicar"),
                    spacing="2",
                ),
                rx.cond(
                    BlogEditFormState.post_publish_active,
                    rx.hstack(
                        rx.input(
                            name="publish_date",
                            type="date", 
                        ),
                        rx.input(
                            name="publish_time",
                            type="time",
                        ),
                        width="100%"
                    ),
                ),
                rx.button("Guardar Cambios", type="submit"),
                spacing="4",
            ),
            on_submit=BlogEditFormState.handle_submit,
        ),
        rx.center(rx.spinner(), height="50vh")
    )