# likemodas/blog/forms.py

import reflex as rx
from .state import BlogAddFormState, BlogEditFormState, BlogPostState
from ..models import Category # Import Category

# --- ✨ DATA LISTS FOR SELECTORS ---
LISTA_TIPOS_ROPA = [
    "Abrigo", "Blusa", "Body", "Buzo", "Camisa", "Camiseta", "Cárdigan", "Chaleco", 
    "Chaqueta", "Conjunto", "Corsé", "Falda", "Gabardina", "Jeans", "Jogger", 
    "Leggings", "Overol", "Pantalón", "Polo", "Short", "Sudadera", "Suéter", 
    "Top", "Vestido", "Otro"
]
LISTA_TIPOS_ZAPATOS = [
    "Baletas", "Botas", "Botines", "Chanclas", "Mocasines", "Pantuflas", 
    "Sandalias", "Tenis", "Zapatillas", "Zapatos de Tacón", "Zuecos", "Otro"
]
LISTA_TIPOS_MOCHILAS = [
    "Antirrobo", "Bandolera", "Bolsa de Lona", "Deportiva", "Escolar", "Maletín",
    "Mochila de Acampada", "Mochila de Viaje", "Mochila Urbana", "Morral", "Otro"
]

def blog_post_add_form() -> rx.Component:
    """The redesigned form for adding a new product."""
    return rx.form(
        rx.vstack(
            rx.heading("Añadir Nuevo Producto", size="8", margin_bottom="1em"),
            rx.grid(
                # --- Left Column: Image Upload and Core Info ---
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
                                width="100%"
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
                        )
                    ),
                    spacing="5",
                ),

                # --- Right Column: Product Details ---
                rx.vstack(
                    rx.input(
                        placeholder="Nombre del producto", value=BlogAddFormState.title, on_change=BlogAddFormState.set_title,
                        required=True, size="3",
                    ),
                    rx.hstack(
                        rx.input(
                            placeholder="Precio", type="number", value=BlogAddFormState.price.to_string(),
                            on_change=BlogAddFormState.set_price_from_input, required=True, size="3"
                        ),
                        rx.select(
                            BlogPostState.categories, placeholder="Selecciona una categoría...", value=BlogAddFormState.category,
                            on_change=BlogAddFormState.set_category, required=True, size="3"
                        ),
                        spacing="4"
                    ),
                    rx.text_area(
                        placeholder="Descripción del producto...", value=BlogAddFormState.content, on_change=BlogAddFormState.set_content,
                        required=True, size="2", style={"height": "150px"}
                    ),
                    spacing="4",
                    align_items="stretch"
                ),
                
                # --- Conditional Fields Section (spans both columns) ---
                rx.vstack(
                     # --- ROPA FIELDS ---
                    rx.cond(
                        BlogAddFormState.category == Category.ROPA.value,
                        rx.grid(
                            rx.select(LISTA_TIPOS_ROPA, placeholder="Tipo de Prenda", value=BlogAddFormState.tipo_prenda, on_change=BlogAddFormState.set_tipo_prenda, size="2"),
                            rx.input(placeholder="Color", value=BlogAddFormState.color_ropa, on_change=BlogAddFormState.set_color_ropa, size="2"),
                            rx.input(placeholder="Talla (S, M, L...)", value=BlogAddFormState.talla, on_change=BlogAddFormState.set_talla, size="2"),
                            rx.input(placeholder="Tipo de Tela", value=BlogAddFormState.tipo_tela, on_change=BlogAddFormState.set_tipo_tela, size="2"),
                            columns="2", spacing="4", width="100%"
                        )
                    ),
                    # --- CALZADO FIELDS ---
                    rx.cond(
                        BlogAddFormState.category == Category.CALZADO.value,
                        rx.grid(
                            rx.select(LISTA_TIPOS_ZAPATOS, placeholder="Tipo de Zapato", value=BlogAddFormState.tipo_zapato, on_change=BlogAddFormState.set_tipo_zapato, size="2"),
                            rx.input(placeholder="Color", value=BlogAddFormState.color_calzado, on_change=BlogAddFormState.set_color_calzado, size="2"),
                            rx.input(placeholder="Número (38, 39...)", value=BlogAddFormState.numero_calzado, on_change=BlogAddFormState.set_numero_calzado, size="2"),
                            rx.input(placeholder="Material", value=BlogAddFormState.material_calzado, on_change=BlogAddFormState.set_material_calzado, size="2"),
                            columns="2", spacing="4", width="100%"
                        )
                    ),
                    # --- MOCHILAS FIELDS ---
                    rx.cond(
                        BlogAddFormState.category == Category.MOCHILAS.value,
                        rx.grid(
                            rx.select(LISTA_TIPOS_MOCHILAS, placeholder="Tipo de Mochila", value=BlogAddFormState.tipo_mochila, on_change=BlogAddFormState.set_tipo_mochila, size="2"),
                            rx.input(placeholder="Material", value=BlogAddFormState.material_mochila, on_change=BlogAddFormState.set_material_mochila, size="2"),
                            rx.input(placeholder="Medidas (e.g., 50x30cm)", value=BlogAddFormState.medidas, on_change=BlogAddFormState.set_medidas, size="2"),
                            columns="2", spacing="4", width="100%"
                        )
                    ),
                    grid_column="span 2",
                    margin_top="1em"
                ),
                columns={"base": "1", "md": "2"},
                spacing="6",
                width="100%"
            ),

            # --- Submission Buttons ---
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
    return rx.cond(
        BlogEditFormState.post,
        rx.form(
            rx.vstack(
                # ID oculto
                rx.input(
                    type="hidden",
                    name="post_id",
                    value=rx.cond(
                        BlogEditFormState.post.id,
                        BlogEditFormState.post.id,
                        ""
                    ),
                ),
                # Título
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
                # Precio (CORREGIDO)
                rx.input(
                    name="price",
                    value=BlogEditFormState.price_str,
                    on_change=BlogEditFormState.set_price,
                    placeholder="Precio",
                    required=True,
                    width="100%",
                ),
                # Contenido
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
                # Switch para publicar
                rx.flex(
                    rx.switch(
                        name="publish_active",
                        is_checked=BlogEditFormState.post_publish_active,
                        on_change=BlogEditFormState.set_post_publish_active,
                    ),
                    rx.text("Publicar"),
                    spacing="2",
                ),
                # Campos de fecha y hora si se publica
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