# full_stack_python/blog/edit.py

import reflex as rx
import reflex_local_auth
from ..ui.base import base_page
from . import forms
from .state import BlogEditFormState
from ..ui.components import not_found_component

@reflex_local_auth.require_login
def blog_post_edit_page() -> rx.Component:
    """
    Página para editar una publicación.
    El formulario se crea DENTRO de rx.cond para asegurar que 'post' existe.
    """
    post = BlogEditFormState.post
    
    # El Vstack contiene toda la lógica de la página de edición.
    edit_view = rx.vstack(
        rx.heading("Editando: ", post.title, size="9"),
        
        # Mantenemos tu diseño responsive, pero ahora se crea de forma segura.
        rx.desktop_only(
            rx.box(forms.blog_post_edit_form(), width="50vw")
        ),
        rx.tablet_only(
            rx.box(forms.blog_post_edit_form(), width="75vw")
        ),
        rx.mobile_only(
            rx.box(forms.blog_post_edit_form(), id="my-form-box", width="85vw")
        ),
        
        spacing="5",
        align="center",
        min_height="95vh",
    )
    
    return base_page(
        # La condición principal: si no hay post, muestra "no encontrado".
        # Si hay post, muestra la vista de edición.
        rx.cond(
            post,
            edit_view,
            not_found_component(title="Publicación no encontrada")
        )
    )