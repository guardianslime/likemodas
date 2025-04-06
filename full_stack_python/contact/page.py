import reflex as rx 
from .. import navigation
from ..ui.base import base_page
from . import form, state

def contact_entries_list_page() -> rx.Component:
    my_child = rx.vstack(
            rx.heading("Contact Entries", size="5"),
            spacing="5",
            align="center",
            min_height="85vh",
    )
    return base_page(my_child)

def contact_page() -> rx.Component:
    my_child = rx.vstack(
            rx.heading("Contact us", size="9"),
            rx.cond(state.ContactState.did_submit, state.ContactState.thank_you, ""),
            rx.desktop_only(
                rx.box(
                    form.contact_form(),
                    width="50vw"
                )
            ),
            rx.tablet_only(
                rx.box(
                    form.contact_form(),
                    width="75vw"
                )
            ),
            rx.mobile_only(
                rx.box(
                    form.contact_form(),
                    id= "my-form-box",
                    width="85vw"
                )
            ),
            spacing="5",
            justify="center",
            align="center",
            min_height="85vh",
            id='my-child'
        )
    
    return base_page(my_child)