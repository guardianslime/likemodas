import reflex as rx
import reflex_local_auth

from full_stack_python.ui.components import not_found_component
from ..ui.base import base_page


from . import forms

from .state import BlogEditFormState
from .notfound import blog_post_not_found

@reflex_local_auth.require_login
def blog_post_edit_page() -> rx.Component:
    my_form = forms.blog_post_edit_form()
    post = BlogEditFormState.post
    my_child = rx.cond(post,
            rx.vstack(
                rx.heading("Editing ", post.title, size="9"), 
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
            ), 
            blog_post_not_found()
        )
    return base_page(
        rx.cond(
            post,
            # Si el post existe, muestra el Vstack con el título y el formulario.
            rx.vstack(
                rx.heading("Editando: ", post.title, size="9"),
                
                # El formulario se crea aquí, solo cuando es seguro hacerlo.
                forms.blog_post_edit_form(),

                spacing="5",
                align="center",
                min_height="95vh",
            ),
            # Si el post no existe, muestra el componente "no encontrado".
            not_found_component(title="Publicación no encontrada")
        )
    )