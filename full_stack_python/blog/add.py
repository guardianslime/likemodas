# full_stack_python/blog/add.py

import reflex as rx 
import reflex_local_auth
from ..ui.base import base_page
from . import forms
from ..auth.state import SessionState # <-- AÑADIR IMPORT

# --- ARREGLO ---
@reflex_local_auth.require_login(on_load=SessionState.on_load)
def blog_post_add_page() -> rx.Component:
    my_form = forms.blog_post_add_form()
    my_child = rx.vstack(
            rx.heading("New Blog Post", size="9"), 
            rx.desktop_only(
                rx.box(
                    my_form,
                    width="50vw"
                )
            ),
            rx.tablet_only(
                rx.box(
                    my_form,
                    width="75vw"
                )
            ),
            rx.mobile_only(
                rx.box(
                    my_form,
                    id= "my-form-box",
                    width="85vw"
                )
            ),
            spacing="5",
            align="center",
            min_height="95vh",
        )
    
    return base_page(my_child)