# likemodas/blog/forms.py (VERSIÓN CON CAMPOS DE TEXTO CENTRADOS Y AMPLIADOS)

import reflex as rx
from ..state import AppState
from ..models import Category
from ..ui.components import searchable_select

def blog_post_add_form() -> rx.Component:
    """Formulario para añadir productos con la estética y centrado corregidos."""
    return rx.form(
        rx.vstack(
            rx.heading("Añadir Nuevo Producto", size="8", margin_bottom="1em"),
            rx.grid(
                # Columna Izquierda: Carga de Imágenes
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
                    align_items="start"
                ),
                # Columna Derecha: Campos de Texto
                rx.vstack(
                    rx.vstack(
                        rx.text("Título del Producto", as_="div", size="2", weight="bold"),
                        rx.input(placeholder="Nombre del producto", name="title", required=True, size="3"),
                        align_items="start", width="100%"
                    ),
                    rx.vstack(
                        rx.text("Categoría", as_="div", size="2", weight="bold"),
                        rx.select(AppState.categories, placeholder="Selecciona una categoría...", name="category", required=True, size="3"),
                        align_items="start", width="100%"
                    ),
                    rx.vstack(
                        rx.text("Precio (COP)", as_="div", size="2", weight="bold"),
                        rx.input(placeholder="Ej: 55000 (sin puntos)", type="number", name="price", required=True, size="3"),
                        align_items="start", width="100%"
                    ),
                    rx.vstack(
                        rx.text("Descripción", as_="div", size="2", weight="bold"),
                        rx.text_area(placeholder="Detalles del producto...", name="content", required=True, size="2", style={"height": "160px"}),
                        align_items="start", width="100%"
                    ),
                    spacing="4", align_items="stretch"
                ),
                grid_template_columns="1.2fr 1fr", spacing="6", width="100%"
            ),
            # Fila del Botón
            rx.hstack(
                rx.button("Publicar Ahora", type="submit", color_scheme="green", size="3"),
                spacing="4", width="100%", justify="end", margin_top="2em"
            ),
            spacing="5",
            # --- ✅ CAMBIO CLAVE AQUÍ ---
            # Se eliminó 'width="100%"' para permitir que el componente se centre.
            max_width="960px",
        ),
        on_submit=AppState.submit_and_publish,
        reset_on_submit=True,
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