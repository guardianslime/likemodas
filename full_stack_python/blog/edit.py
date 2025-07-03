# full_stack_python/blog/edit.py

import reflex as rx
import reflex_local_auth
from ..ui.base import base_page
from .forms import blog_post_edit_form
from .state import BlogEditFormState
from .notfound import blog_post_not_found

@reflex_local_auth.require_login
def blog_post_edit_page() -> rx.Component:
    """Página para editar un artículo existente."""
    post = BlogEditFormState.post
    my_child = rx.cond(
        post,
        rx.vstack(
            rx.heading("Editando: ", rx.code(post.title, variant="soft"), size="8"),
            rx.box(
                blog_post_edit_form(),
                width=["90vw", "75vw", "50vw"] # Responsive width
            ),
            spacing="5",
            align="center",
            min_height="95vh",
        ),
        blog_post_not_found()
    )
    return base_page(my_child)