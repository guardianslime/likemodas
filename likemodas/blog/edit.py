# likemodas/blog/edit.py (CORREGIDO)

import reflex as rx
from ..auth.admin_auth import require_admin
from . import forms
from .state import BlogEditFormState

@require_admin
def blog_post_edit_content() -> rx.Component:
    return rx.vstack(
        rx.heading("Editando Post", size="7"),
        forms.blog_post_edit_form(),
        width="100%",
        max_width="760px",
        margin="auto",
    )