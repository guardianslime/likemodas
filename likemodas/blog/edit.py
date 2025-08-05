# likemodas/blog/edit.py (CORREGIDO)

import reflex as rx
from ..auth.admin_auth import require_admin
from .forms import blog_post_edit_form

@require_admin
def blog_post_edit_content() -> rx.Component:
    return rx.vstack(
        rx.heading("Editando Post", size="7"),
        blog_post_edit_form(),
        width="100%",
        max_width="760px",
        margin="auto",
    )