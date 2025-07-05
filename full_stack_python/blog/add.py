import reflex as rx
import reflex_local_auth
from ..ui.base import base_page
from .forms import blog_post_form
from .state import BlogPostState

@reflex_local_auth.require_login
def blog_post_add_page() -> rx.Component:
    return base_page(
        rx.vstack(
            rx.heading("Crear Nueva Publicación", size="9"),
            blog_post_form(),
            width=["95%", "80%", "70%"],
            margin="auto",
            spacing="5"
        ),
        # Limpiamos el estado al montar la página de "crear"
        on_mount=BlogPostState.get_post_detail
    )