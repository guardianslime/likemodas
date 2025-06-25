import reflex as rx
import reflex_local_auth
from ..ui.base import base_page


from . import forms

from .state import ContactEditFormState
from .notfound import contact_entry_not_found

@reflex_local_auth.require_login
def contact_entry_edit_page() -> rx.Component:
    my_form = forms.contact_entry_edit_form()
    entry = ContactEditFormState.entry
    my_child = rx.cond(entry,
            rx.vstack(
                rx.heading("Editing ", entry.title, size="9"), 
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
            contact_entry_not_found()
        )
    return base_page(my_child)