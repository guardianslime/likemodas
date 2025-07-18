# full_stack_python/blog/edit.py (CORREGIDO)
import reflex as rx
# --- ✨ CAMBIO: Se importa el decorador de admin ---
from ..auth.admin_auth import require_admin
from ..ui.base import base_page
from . import forms
from .state import BlogEditFormState

# --- ✨ CAMBIO: Se usa el decorador de admin ---
@require_admin
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