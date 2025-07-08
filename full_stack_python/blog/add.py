# full_stack_python/blog/add.py (VERSIÓN UNIFICADA)
import reflex as rx
import reflex_local_auth
from .forms import blog_post_add_form
from ..ui.base import base_page
from . import forms

@reflex_local_auth.require_login
def blog_post_add_page() -> rx.Component:
    return base_page(
        rx.center(
            blog_post_add_form(),
            min_height="85vh",
            padding="2em",
        )
    )