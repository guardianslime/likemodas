# likemodas/blog/forms.py (CORREGIDO)

import reflex as rx
from ..state import AppState
from ..models import Category
from ..ui.components import searchable_select

def blog_post_add_form() -> rx.Component:
    """Formulario para añadir productos, ahora usando AppState."""
    
    # Esta sección ahora depende de que tengas los métodos y variables
    # correspondientes en tu AppState (ej. AppState.category, AppState.tipo_prenda, etc.)
    # Asegúrate de agregar las variables y métodos de BlogAddFormState a tu AppState.
    characteristics_section = rx.vstack(
        rx.heading("Características", size="5", width="100%"),
        rx.divider(),
        rx.cond(
            AppState.category == Category.ROPA.value,
            rx.grid(
                # Ejemplo para "Tipo de Prenda"
                # Necesitarás propiedades como AppState.filtered_tipos_ropa en tu AppState
                # y métodos como AppState.set_tipo_prenda
                searchable_select(placeholder="Tipo de Prenda", options=AppState.filtered_tipos_ropa, on_change_select=AppState.set_tipo_prenda, value_select=AppState.tipo_prenda, search_value=AppState.search_add_tipo_prenda, on_change_search=AppState.set_search_add_tipo_prenda, filter_name="add_form_tipo_prenda"),
                # ... y así para los demás selects
                columns="2", spacing="4", width="100%"
            )
        ),
        # ... resto de las condiciones para CALZADO y MOCHILAS ...
        align_items="start", width="100%"
    )

    upload_section = rx.card(
        rx.vstack(
            rx.upload(
                rx.vstack(rx.icon("upload", size=32), rx.text("Subir imágenes")),
                id="blog_upload", multiple=True, max_files=5, accept={"image/*": [".jpg", ".png", ".jpeg", ".webp"]},
                on_drop=AppState.handle_upload(rx.upload_files("blog_upload")),
                border="2px dashed #ccc", padding="2em", width="100%"
            ),
            rx.cond(
                AppState.temp_images,
                rx.grid(
                    rx.foreach(
                        AppState.temp_images,
                        lambda img: rx.box(
                            rx.image(src=rx.get_upload_url(img), width="100%", height="100%", object_fit="cover", border_radius="md"),
                            rx.icon(tag="trash", on_click=AppState.remove_image(img), color="red", style={"position": "absolute", "top": "5px", "right": "5px", "cursor": "pointer"}),
                            style={"position": "relative"},
                        ),
                    ),
                    columns="3", spacing="2", width="100%", padding_top="0.5em",
                )
            ),
            spacing="4",
        )
    )

    basic_info_section = rx.vstack(
        rx.input(placeholder="Nombre del producto", value=AppState.title, on_change=AppState.set_title, required=True, size="3"),
        rx.select(
            AppState.categories, # Necesitarás esta propiedad en AppState
            placeholder="Selecciona una categoría...",
            value=AppState.category,
            on_change=AppState.set_category,
            required=True, size="3", width="100%"
        ),
        rx.input(placeholder="Precio (ej: 55000)", type="number", value=AppState.price.to_string(), on_change=AppState.set_price_from_input, required=True, size="3", width="100%"),
        rx.text_area(placeholder="Descripción del producto...", value=AppState.content, on_change=AppState.set_content, required=True, size="2", style={"height": "200px"}),
        spacing="4", align_items="stretch"
    )

    return rx.form(
        rx.vstack(
            rx.heading("Añadir Nuevo Producto", size="8", margin_bottom="1em"),
            rx.grid(
                rx.vstack(upload_section, align_items="stretch"),
                rx.vstack(basic_info_section, align_items="stretch"),
                rx.vstack(characteristics_section, grid_column="span 2", margin_top="1em"),
                grid_template_columns="1.2fr 1fr", spacing="6", width="100%"
            ),
            rx.hstack(
                rx.button("Guardar Borrador", on_click=AppState.submit_draft, variant="soft", size="3"),
                rx.button("Publicar Ahora", on_click=AppState.submit_and_publish, color_scheme="green", size="3"),
                spacing="4", width="100%", justify="end", margin_top="2em"
            ),
            spacing="5", width="100%", max_width="1600px", padding="2em",
        ),
    )


def blog_post_edit_form() -> rx.Component:
    """Formulario para editar posts, ahora usando AppState."""
    return rx.cond(
        AppState.post, # Asumiendo que `post` es la variable para el post que se edita
        rx.form(
            rx.vstack(
                rx.input(name="title", value=AppState.post_title, on_change=AppState.set_post_title, placeholder="Título del Post", required=True, width="100%"),
                rx.input(name="price", value=AppState.price_str, on_change=AppState.set_price, placeholder="Precio", required=True, width="100%"),
                rx.text_area(
                    name="content", value=AppState.post_content, on_change=AppState.set_post_content,
                    placeholder="Escribe tu contenido aquí...", required=True, height="40vh", width="100%"
                ),
                rx.button("Guardar Cambios", type="submit"),
                spacing="4",
            ),
            on_submit=AppState.handle_edit_submit,
        ),
        rx.center(rx.spinner(), height="50vh")
    )