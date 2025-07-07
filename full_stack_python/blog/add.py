# full_stack_python/blog/add.py

import reflex as rx
import reflex_local_auth
from ..ui.base import base_page
from .state import BlogAddPostFormState

def image_preview_component(img_name: str) -> rx.Component:
    """Componente para previsualizar una imagen temporal con botón de borrado."""
    return rx.box(
        rx.image(src=rx.get_upload_url(img_name), height="10em", width="auto"),
        rx.icon(
            tag="trash",
            on_click=BlogAddPostFormState.eliminar_imagen_temp(img_name),
            style={
                "position": "absolute", "top": "0.5em", "right": "0.5em",
                "cursor": "pointer", "color": "red", "background": "white",
                "borderRadius": "50%", "padding": "0.2em"
            }
        ),
        position="relative",
        padding="0.5em"
    )

def blog_post_add_form() -> rx.Component:
    """Formulario para añadir un post con carga de imágenes."""
    return rx.form(
        rx.vstack(
            rx.input(name="title", placeholder="Título de la publicación", required=True, width="100%"),
            rx.text_area(name="content", placeholder="Escribe tu contenido aquí...", required=True, height='30vh', width='100%'),
            rx.upload(
                rx.text("Arrastra imágenes o haz clic para seleccionarlas.", text_align="center"),
                id="image_upload",
                border="2px dashed #60a5fa",
                padding="2em",
                multiple=True,
                accept={
                    "image/png": [".png"], "image/jpeg": [".jpg", ".jpeg"],
                    "image/gif": [".gif"], "image/webp": [".webp"],
                },
                on_drop=BlogAddPostFormState.handle_upload(rx.upload_files(upload_id="image_upload")),
            ),
            rx.text("Imágenes para publicar:"),
            rx.flex(
                rx.foreach(BlogAddPostFormState.imagenes_temporales, image_preview_component),
                wrap="wrap",
                spacing="2",
            ),
            rx.button(
                "Publicar",
                type="submit",
                disabled=~BlogAddPostFormState.is_hydrated, # Deshabilitado mientras se procesa
                width="100%",
                size="3"
            ),
            spacing="4",
            width="100%"
        ),
        on_submit=BlogAddPostFormState.handle_submit,
        reset_on_submit=True,
        width="100%"
    )

@reflex_local_auth.require_login
def blog_post_add_page() -> rx.Component:
    my_child = rx.vstack(
        rx.heading("Crear Nueva Publicación", size="8", margin_bottom="1em"),
        rx.box(
            blog_post_add_form(),
            width=["90vw", "80vw", "70vw", "60vw"] # Responsive width
        ),
        spacing="5",
        align="center",
        min_height="95vh",
    )
    return base_page(my_child)