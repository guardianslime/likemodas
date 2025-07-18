# full_stack_python/blog/add.py (CORREGIDO)
import reflex as rx
# --- ✨ CAMBIO: Se importa el decorador de admin ---
from ..auth.admin_auth import require_admin
from .forms import blog_post_add_form
from ..ui.base import base_page
from . import forms

# --- ✨ CAMBIO: Se usa el decorador de admin ---
@require_admin
def blog_post_add_page() -> rx.Component:
    return base_page(
        rx.center(
            blog_post_add_form(),
            min_height="85vh",
            padding="2em",
        )
    )