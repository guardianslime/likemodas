# full_stack_python/blog/edit.py

import reflex as rx
import reflex_local_auth
from ..ui.base import base_page

from . import forms
# Importa el estado unificado
from .state import BlogPostState
from .notfound import blog_post_not_found

@reflex_local_auth.require_login
def blog_post_edit_page() -> rx.Component:
    my_child = rx.cond(
        # Comprueba contra el estado unificado
        BlogPostState.post,
        rx.vstack(
            rx.heading("Editando ", BlogPostState.post.title, size="9"),
            rx.box(
                forms.blog_post_edit_form(),
                width=["90vw", "80vw", "70vw", "60vw"]
            ),
            spacing="5",
            align="center",
            min_height="95vh",
        ),
        rx.center(
            rx.spinner(size="3"),
            height="95vh"
        )
    )
    return base_page(my_child)