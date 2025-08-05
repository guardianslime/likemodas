# likemodas/blog/add.py (CORREGIDO)

import reflex as rx
from ..auth.admin_auth import require_admin
from .forms import blog_post_add_form

@require_admin
def blog_post_add_content() -> rx.Component:
    return rx.center(
        blog_post_add_form(),
        min_height="85vh",
        padding="2em",
    )