# full_stack_python/blog/add.py
import reflex as rx
import reflex_local_auth
from ..ui.base import base_page
from .forms import blog_post_form

@reflex_local_auth.require_login
def blog_post_add_page() -> rx.Component:
    return base_page(
        rx.vstack(
            rx.heading("Crear Nueva Publicación", size="9"),
            blog_post_form(), # Usamos el formulario unificado
            width=["90%", "80%", "60%"],
            margin="auto",
            spacing="5"
        )
    )