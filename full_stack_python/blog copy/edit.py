import reflex as rx
import reflex_local_auth
from ..ui.base import base_page


from . import forms

from .state import ContactEditFormState
from .notfound import contact_post_not_found

@reflex_local_auth.require_login
def blog_post_edit_page() -> rx.Component:
    my_form = forms.contact_post_edit_form()
    post = ContactEditFormState.post
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
            contact_post_not_found()
        )
    return base_page(my_child)