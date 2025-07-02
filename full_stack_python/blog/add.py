# add.py

import reflex as rx 
import reflex_local_auth

from ..ui.base import base_page
from . import forms
# 👇 CORRECCIÓN AQUÍ: Importa el nombre correcto del estado
from .state import BlogAddPostFormState

@reflex_local_auth.require_login
def blog_post_add_page() -> rx.Component:
    my_form = forms.blog_post_add_form()
    
    image_uploader = rx.vstack(
        rx.upload(
            rx.text("Arrastra aquí tu imagen JPG/PNG o haz clic para seleccionar"),
            border="2px dotted rgb(107, 114, 128)",
            padding="2em",
            width="100%",
            accept={
                "image/png": [".png"],
                "image/jpeg": [".jpg", ".jpeg"],
            },
            # 👇 CORRECCIÓN AQUÍ: Usa el estado correcto
            on_drop=BlogAddPostFormState.handle_upload(rx.upload_files()),
        ),
        rx.cond(
            # 👇 CORRECCIÓN AQUÍ: Usa el estado correcto
            BlogAddPostFormState.uploaded_image_url,
            rx.box(
                rx.text("Vista Previa:", weight="bold", margin_bottom="0.5em"),
                rx.image(
                    src=BlogAddPostFormState.uploaded_image_url,
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
            rx.vstack(
                image_uploader,
                my_form,
                spacing="5",
                width=["85vw", "75vw", "50vw"]
            ),
            spacing="5",
            align="center",
            min_height="95vh",
        )
    
    return base_page(my_child)