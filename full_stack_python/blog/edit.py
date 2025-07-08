# full_stack_python/blog/edit.py

import reflex as rx
import reflex_local_auth
from ..ui.base import base_page

from . import forms
from .state import BlogEditFormState  # Importa el estado específico
from .notfound import blog_post_not_found

@reflex_local_auth.require_login
def blog_post_edit_page() -> rx.Component:
    my_child = rx.cond(
        BlogEditFormState.post,  # Comprueba directamente la variable de estado
        rx.vstack(
            # --- CORRECCIÓN ---
            # Accede al título directamente desde el estado para mayor seguridad
            rx.heading("Editing ", BlogEditFormState.post.title, size="9"),
            rx.desktop_only(
                rx.box(
                    forms.blog_post_edit_form(),
                    width="50vw"
                )
            ),
            rx.tablet_only(
                rx.box(
                    forms.blog_post_edit_form(),
                    width="75vw"
                )
            ),
            rx.mobile_only(
                rx.box(
                    forms.blog_post_edit_form(),
                    id="my-form-box",
                    width="85vw"
                )
            ),
            spacing="5",
            align="center",
            min_height="95vh",
        ),
        blog_post_not_found()
    )
    return base_page(my_child)