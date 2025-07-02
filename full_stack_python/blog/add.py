import reflex as rx 
import reflex_local_auth
from ..ui.base import base_page
from . import forms
from .state import BlogPostAddState # 1. Importa el nuevo estado

@reflex_local_auth.require_login
def blog_post_add_page() -> rx.Component:
    my_form = forms.blog_post_add_form()
    
    # 2. Componente de subida y vista previa de imagen
    image_uploader = rx.vstack(
        rx.upload(
            rx.text("Arrastra aquí tu imagen JPG/PNG o haz clic para seleccionar"),
            border="2px dotted rgb(107, 114, 128)",
            padding="2em",
            width="100%",
            # Define los tipos de archivo aceptados
            accept={
                "image/png": [".png"],
                "image/jpeg": [".jpg", ".jpeg"],
            },
            # Llama a handle_upload cuando se selecciona un archivo
            on_drop=BlogPostAddState.handle_upload(rx.upload_files()),
        ),
        # Muestra la imagen SÓLO si ya se ha subido una
        rx.cond(
            BlogPostAddState.uploaded_image_url,
            rx.box(
                rx.text("Vista Previa:", weight="bold", margin_bottom="0.5em"),
                rx.image(
                    src=BlogPostAddState.uploaded_image_url,
                    height="15em",
                    width="auto",
                    border_radius="10px",
                    border="1px solid #ddd"
                ),
                margin_top="1em"
            )
        ),
        align="center",
        spacing="2",
        width="100%"
    )
    
    my_child = rx.vstack(
            rx.heading("New Blog Post", size="9"),
            
            # 3. Integra el componente de imagen y el formulario
            rx.vstack(
                image_uploader, # Añadido aquí
                my_form,
                spacing="5",
                width=["85vw", "75vw", "50vw"] # Ancho responsivo
            ),

            spacing="5",
            align="center",
            min_height="95vh",
        )
    
    return base_page(my_child)

