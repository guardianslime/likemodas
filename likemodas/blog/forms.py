# likemodas/blog/forms.py (CORREGIDO Y MEJORADO)

import reflex as rx
from ..state import AppState
from ..models import Category
from ..ui.components import searchable_select

def blog_post_add_form() -> rx.Component:
    """Formulario para añadir productos, ahora usando AppState."""
    return rx.form(
        rx.vstack(
            rx.heading("Añadir Nuevo Producto", size="8", margin_bottom="1em"),
            rx.grid(
                rx.vstack(
                    rx.upload(
                        rx.vstack(rx.icon("upload", size=32), rx.text("Subir imágenes")),
                        id="blog_upload", multiple=True, max_files=5,
                        on_drop=AppState.handle_upload(rx.upload_files("blog_upload")),
                        border="2px dashed #ccc", padding="2em", width="100%"
                    ),
                    rx.cond(
                        AppState.temp_images,
                        rx.grid(
                            rx.foreach(
                                AppState.temp_images,
                                lambda img: rx.box(
                                    rx.image(src=rx.get_upload_url(img), width="100px", height="100px"),
                                    rx.icon(tag="trash", on_click=AppState.remove_image(img), cursor="pointer", style={"position": "absolute", "top": "5px", "right": "5px", "color": "white", "background": "rgba(0,0,0,0.5)", "border_radius": "50%"}),
                                    position="relative"
                                ),
                            ),
                            columns="3", spacing="2",
                        )
                    ),
                ),
                rx.vstack(
                    rx.input(placeholder="Nombre del producto", name="title", required=True, size="3"),
                    rx.select(
                        AppState.categories,
                        placeholder="Selecciona una categoría...",
                        name="category",
                        required=True, size="3",
                    ),
                    rx.input(placeholder="Precio (ej: 55000)", type="number", name="price", required=True, size="3"),
                    rx.text_area(placeholder="Descripción...", name="content", required=True, size="2", style={"height": "200px"}),
                    spacing="4", align_items="stretch"
                ),
                grid_template_columns="1.2fr 1fr", spacing="6", width="100%"
            ),
            rx.hstack(
                rx.button("Publicar Ahora", type="submit", color_scheme="green", size="3"),
                spacing="4", width="100%", justify="end", margin_top="2em"
            ),
            spacing="5", width="100%", max_width="1600px", padding="2em",
        ),
        on_submit=AppState.submit_and_publish,
        reset_on_submit=True,
    )

def blog_post_edit_form() -> rx.Component:
    """El formulario para editar una publicación, ahora con gestión de imágenes."""
    return rx.form(
        rx.vstack(
            # --- ✨ SECCIÓN DE GESTIÓN DE IMÁGENES ---
            rx.text("Imágenes Actuales", as_="div", size="2", weight="bold"),
            rx.grid(
                rx.foreach(
                    AppState.images_to_edit,
                    lambda img_url: rx.box(
                        rx.image(src=rx.get_upload_url(img_url), width="100px", height="100px", object_fit="cover"),
                        rx.icon_button(
                            rx.icon("trash-2", size=16),
                            on_click=AppState.remove_edited_image(img_url),
                            color_scheme="red",
                            variant="soft",
                            size="1",
                            style={"position": "absolute", "top": "4px", "right": "4px"}
                        ),
                        position="relative",
                        border="1px solid #ddd",
                        border_radius="md"
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
            rx.cond(
                AppState.new_temp_images,
                rx.grid(
                    rx.foreach(
                        AppState.new_temp_images,
                        lambda img: rx.box(
                            rx.image(src=rx.get_upload_url(img), width="100px", height="100px"),
                            rx.icon(tag="trash", on_click=AppState.remove_new_temp_image(img), cursor="pointer"),
                        ),
                    ),
                    columns="4", spacing="2",
                )
            ),
            # --- FIN DE SECCIÓN DE IMÁGENES ---

            rx.text("Título del Producto", as_="div", size="2", margin_top="1em", weight="bold"),
            rx.input(
                name="title", value=AppState.post_title,
                on_change=AppState.set_post_title, required=True,
            ),
            
            rx.text("Descripción", as_="div", size="2", margin_bottom="2px", weight="bold"),
            rx.text_area(
                name="content", value=AppState.post_content,
                on_change=AppState.set_post_content,
                rows=8, required=True,
            ),

            rx.text("Precio (COP)", as_="div", size="2", margin_bottom="2px", weight="bold"),
            rx.input(
                name="price", value=AppState.price_str,
                on_change=AppState.set_price, type="number", required=True,
            ),
            rx.button("Guardar Cambios", type="submit", width="100%", margin_top="1em", size="3"),
            spacing="4", width="100%"
        ),
        on_submit=AppState.save_edited_post,
        width="100%",
    )