# full_stack_python/blog/edit.py (VERSIÓN UNIFICADA)
import reflex as rx
import reflex_local_auth
from ..ui.base import base_page
from . import forms
from .state import BlogEditFormState

@reflex_local_auth.require_login
def blog_post_edit_page() -> rx.Component:
    return base_page(
        rx.vstack(
            rx.heading("Editando Post", size="7"),
            forms.blog_post_edit_form(),
            width="100%",
            max_width="760px",
            margin="auto",
        )
    )