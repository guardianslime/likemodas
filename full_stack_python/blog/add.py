# full_stack_python/blog/add.py

import reflex as rx
import reflex_local_auth
from ..ui.base import base_page
from .state import BlogAddPostFormState, BlogPostState

# --- COMPONENTE REUTILIZABLE ---
def image_upload_component(State: type[BlogPostState]) -> rx.Component:
    """
    Un componente para subir la imagen del post y mostrar una vista previa.
    Se puede usar tanto al crear como al editar un post.
    """
    return rx.vstack(
        rx.upload.root(
            rx.box(
                rx.icon(tag="cloud_upload", size="3em", color=rx.color("accent", 9)),
                rx.heading("Haz clic o arrastra aquí", size="4", weight="medium"),
                rx.text("SVG, PNG, JPG o GIF (MAX. 5MB)"),
                padding="2em",
                border=f"2px dashed {rx.color('gray', 6)}",
                border_radius="0.5em",
                cursor="pointer",
            ),
            id="my_upload",
            on_drop=State.handle_upload,
            width="100%",
        ),
        rx.flex(
            rx.foreach(
                State.img,
                lambda image: rx.image(src=image, height="8em", width="auto", border_radius="0.5em", box_shadow="sm"),
            ),
            spacing="2",
            margin_top="1rem",
        ),
        align="center",
        spacing="4",
        width="100%",
    )

@reflex_local_auth.require_login
def blog_post_add_page() -> rx.Component:
    """Página para crear un nuevo artículo del blog."""
    my_form = rx.form(
        rx.vstack(
            rx.input(name="title", placeholder="Título del Artículo", required=True, width="100%"),
            rx.heading("Imagen Principal", size="5", margin_top="1em", width="100%", text_align="left"),
            # --- USO DEL COMPONENTE ---
            image_upload_component(BlogAddPostFormState),
            rx.text_area(name="content", placeholder="Escribe tu artículo aquí...", required=True, height='50vh', width='100%', margin_top="1em"),
            rx.button("Guardar y Editar", type="submit", margin_top="1em"),
            spacing="4",
        ),
        on_submit=BlogAddPostFormState.handle_submit,
        reset_on_submit=True,
    )
    
    my_child = rx.vstack(
        rx.heading("Nuevo Artículo", size="9"),
        rx.box(my_form, width=["90vw", "75vw", "50vw"]),
        spacing="5",
        align="center",
        min_height="95vh",
    )
    
    return base_page(my_child)