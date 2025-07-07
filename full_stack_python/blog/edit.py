# full_stack_python/blog/edit.py

import reflex as rx
import reflex_local_auth
from ..ui.base import base_page

from . import forms
from .state import BlogEditFormState
from .notfound import blog_post_not_found

@reflex_local_auth.require_login
def blog_post_edit_page() -> rx.Component:
    # --- LÓGICA CORREGIDA ---
    # Usamos rx.cond para asegurarnos de que el post se haya cargado
    # antes de intentar renderizar el formulario.
    my_child = rx.cond(
        BlogEditFormState.post,
        # Si el post existe, muestra el formulario
        rx.vstack(
            rx.heading("Editando ", BlogEditFormState.post.title, size="9"),
            rx.box(
                forms.blog_post_edit_form(),
                width=["90vw", "80vw", "70vw", "60vw"] # Ancho responsivo
            ),
            spacing="5",
            align="center",
            min_height="95vh",
        ),
        # Si el post aún no carga, muestra un spinner (indicador de carga)
        rx.center(
            rx.spinner(size="3"),
            height="95vh"
        )
    )
    return base_page(my_child)