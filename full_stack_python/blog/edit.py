import reflex as rx
import reflex_local_auth
from ..ui.base import base_page
from . import forms
from .state import BlogEditFormState
from ..ui.components import not_found_component

@reflex_local_auth.require_login
def blog_post_edit_page() -> rx.Component:
    post = BlogEditFormState.post
    
    edit_view = rx.vstack(
        rx.heading("Editando: ", post.title, size="9"),
        rx.desktop_only(rx.box(forms.blog_post_edit_form(), width="50vw")),
        rx.tablet_only(rx.box(forms.blog_post_edit_form(), width="75vw")),
        rx.mobile_only(rx.box(forms.blog_post_edit_form(), id="my-form-box", width="85vw")),
        spacing="5", align="center", min_height="95vh",
    )
    
    return base_page(
        rx.cond(post, edit_view, not_found_component(title="Publicación no encontrada")),
        on_mount=BlogEditFormState.get_post_detail
    )