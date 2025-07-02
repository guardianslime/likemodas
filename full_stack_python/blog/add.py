# full_stack_python/blog/add.py

import reflex as rx
import reflex_local_auth
from ..ui.base import base_page
# Importamos el estado necesario para el formulario
from .state import BlogAddPostFormState

# --- NUEVA UBICACIÓN DEL COMPONENTE DE SUBIDA ---
def image_upload_component(State: rx.State) -> rx.Component:
    """Un componente para subir la imagen del post y mostrar una vista previa."""
    return rx.vstack(
        rx.upload.root(
            rx.box(
                rx.icon(
                    tag="cloud_upload",
                    style={"width": "3rem", "height": "3rem", "color": "#2563eb", "marginBottom": "0.75rem"},
                ),
                rx.hstack(
                    rx.text("Click to upload", style={"fontWeight": "bold", "color": "#1d4ed8"}),
                    " or drag and drop",
                    style={"fontSize": "0.875rem", "color": "#4b5563"},
                ),
                rx.text(
                    "SVG, PNG, JPG or GIF (MAX. 5MB)",
                    style={"fontSize": "0.75rem", "color": "#6b7280", "marginTop": "0.25rem"},
                ),
                style={
                    "display": "flex", "flexDirection": "column", "alignItems": "center",
                    "justifyContent": "center", "padding": "1.5rem", "textAlign": "center",
                },
            ),
            id="my_upload",
            style={
                "maxWidth": "24rem", "height": "16rem", "borderWidth": "2px", "borderStyle": "dashed",
                "borderColor": "#60a5fa", "borderRadius": "0.75rem", "cursor": "pointer",
            },
            on_drop=State.handle_upload,
        ),
        # Vista previa de la imagen que se está subiendo
        rx.flex(
            rx.foreach(
                State.img,
                lambda image: rx.image(src=image, height="8em", width="auto", border_radius="0.5em"),
            ),
            spacing="2",
            margin_top="1rem",
        ),
        align="center",
        spacing="4",
        width="100%",
    )
# ---------------------------------------------


@reflex_local_auth.require_login
def blog_post_add_page() -> rx.Component:
    # --- FORMULARIO INTEGRADO DIRECTAMENTE EN LA PÁGINA ---
    my_form = rx.form(
        rx.vstack(
            rx.input(
                name="title",
                placeholder="Título del Artículo",
                required=True,
                width="100%",
            ),
            rx.heading("Imagen Principal", size="5", margin_top="1em"),
            # Usamos el componente que acabamos de definir en este mismo archivo
            image_upload_component(BlogAddPostFormState),
            rx.text_area(
                name="content",
                placeholder="Escribe tu artículo aquí...",
                required=True,
                height='50vh',
                width='100%',
                margin_top="1em",
            ),
            rx.button("Guardar y Editar", type="submit", margin_top="1em"),
        ),
        on_submit=BlogAddPostFormState.handle_submit,
        reset_on_submit=True,
    )
    # ----------------------------------------------------
    
    my_child = rx.vstack(
        rx.heading("New Blog Post", size="9"),
        rx.desktop_only(
            rx.box(
                my_form,
                width="50vw"
            )
        ),
        rx.tablet_only(
            rx.box(
                my_form,
                width="75vw"
            )
        ),
        rx.mobile_only(
            rx.box(
                my_form,
                id= "my-form-box",
                width="85vw"
            )
        ),
        spacing="5",
        align="center",
        min_height="95vh",
    )
    
    return base_page(my_child)