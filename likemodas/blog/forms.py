import reflex as rx
from .state import BlogAddFormState, BlogEditFormState, BlogPostState, SessionState
from ..models import Category
from ..data.product_options import LISTA_TIPOS_ROPA, LISTA_TIPOS_ZAPATOS, LISTA_TIPOS_MOCHILAS
from ..ui.components import searchable_select

def blog_post_add_form() -> rx.Component:
    """El formulario rediseñado para añadir un nuevo producto con diseño y proporciones mejoradas."""
    return rx.form(
        rx.vstack(
            rx.heading("Añadir Nuevo Producto", size="8", margin_bottom="1em"),
            rx.grid(
                # --- Columna izquierda: Carga de imágenes ---
                rx.vstack(
                    rx.card(
                        rx.vstack(
                            rx.upload(
                                rx.vstack(
                                    rx.icon("upload", size=32),
                                    rx.text("Subir imágenes del producto"),
                                ),
                                id="blog_upload",
                                multiple=True,
                                max_files=5,
                                accept={"image/*": [".jpg", ".png", ".jpeg", ".webp"]},
                                on_drop=BlogAddFormState.handle_upload(rx.upload_files("blog_upload")),
                                border="2px dashed #ccc",
                                padding="2em",
                                width="100%",
                                height="100%",
                            ),
                            rx.cond(
                                BlogAddFormState.temp_images,
                                rx.hstack(
                                    rx.foreach(
                                        BlogAddFormState.temp_images,
                                        lambda img: rx.box(
                                            rx.image(src=rx.get_upload_url(img), width="100px", height="100px", object_fit="cover", border_radius="md"),
                                            rx.icon(tag="trash", on_click=BlogAddFormState.remove_image(img), color="red", style={"position": "absolute", "top": "5px", "right": "5px", "cursor": "pointer"}),
                                            style={"position": "relative", "margin": "0.5em"},
                                        ),
                                    ),
                                    wrap="wrap",
                                    spacing="3"
                                )
                            ),
                            spacing="4",
                            height="100%",
                            justify_content="center",
                        ),
                        height="100%",
                    ),
                    spacing="5",
                    height="100%",
                ),

                # --- Columna derecha: Detalles del producto ---
                rx.vstack(
                    rx.input(placeholder="Nombre del producto", value=BlogAddFormState.title, on_change=BlogAddFormState.set_title, required=True, size="3"),
                    rx.hstack(
                        rx.input(placeholder="Precio", type="number", value=BlogAddFormState.price.to_string(), on_change=BlogAddFormState.set_price_from_input, required=True, size="3"),
                        rx.select(BlogPostState.categories, placeholder="Selecciona una categoría...", value=BlogAddFormState.category, on_change=BlogAddFormState.set_category, required=True, size="3"),
                        spacing="4"
                    ),
                    rx.text_area(placeholder="Descripción del producto...", value=BlogAddFormState.content, on_change=BlogAddFormState.set_content, required=True, size="2", style={"height": "100%"}), # Alto al 100%
                    spacing="4",
                    align_items="stretch",
                    height="100%", # Ocupa todo el alto
                ),
                
                # --- Sección de características adicionales ---
                rx.vstack(
                    rx.cond(
                        BlogAddFormState.category != "",
                        rx.hstack(
                            rx.text("Características Adicionales", weight="bold"),
                            rx.spacer(),
                            rx.button(
                                "Limpiar",
                                on_click=BlogAddFormState.clear_all_attributes,
                                size="1",
                                variant="soft",
                                color_scheme="gray"
                            ),
                            justify="between",
                            align_items="center",
                            width="100%",
                            margin_bottom="0.5em"
                        ),
                    ),
                    # ... (El código de los campos condicionales no cambia) ...
                    grid_column="span 2",
                    margin_top="1em"
                ),

                # --- ✨ CAMBIO PRINCIPAL: Se define la proporción de las columnas ---
                # En pantallas medianas (md) y grandes, la 2da columna será el doble de ancha que la 1ra.
                # En pantallas pequeñas (base), habrá solo 1 columna.
                grid_template_columns={"base": "1fr", "md": "1fr 2fr"},
                align_items="stretch", 
                spacing="6",
                width="100%"
            ),

            # --- Botones de envío ---
            rx.hstack(
                rx.button("Guardar Borrador", on_click=BlogAddFormState.submit, variant="soft", size="3"),
                rx.button("Publicar Ahora", on_click=BlogAddFormState.submit_and_publish, color_scheme="green", size="3"),
                spacing="4", width="100%", justify="end", margin_top="2em"
            ),
            
            spacing="5",
            width="100%",
            max_width="1200px",
            padding="2em",
        ),
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