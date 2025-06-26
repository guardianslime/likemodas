# full_stack_python/contact/page.py

import reflex as rx 
import reflex_local_auth
from ..ui.base import base_page
from ..models import ContactEntryModel
from . import form, state

def contact_entry_list_item(contact: ContactEntryModel):
    """Muestra una entrada de contacto individual."""
    return rx.box(
        rx.heading(f"{contact.first_name} ({contact.email})"),
        rx.text(contact.message, white_space="pre-wrap"),
        rx.text(f"Received on: {contact.created_at.strftime('%Y-%m-%d %H:%M')}" ),
        # Verifica si la entrada de contacto está asociada a un usuario.
        rx.cond(
            contact.userinfo_id,
            rx.text("Submitted by logged-in user, ID:", f"{contact.userinfo_id}"),
            rx.text("Submitted by a guest."),
        ),
        padding="1em",
        border="1px solid #eee",
        border_radius="0.5em"
    )

# ¡CORRECCIÓN! Se añade el decorador para requerir inicio de sesión.
@reflex_local_auth.require_login
def contact_entries_list_page() -> rx.Component:
    return base_page(
        rx.vstack(
            rx.heading("Contact Entries", size="5"),
            rx.foreach(
                state.ContactState.entries,
                contact_entry_list_item
            ),
            spacing="5",
            align="center",
            min_height="85vh",
        )
    )

def contact_page() -> rx.Component:
    my_child = rx.vstack(
            rx.heading("Contact us", size="9"),
            rx.cond(state.ContactState.did_submit, state.ContactState.thank_you, form.contact_form()),
            spacing="5",
            justify="center",
            align="center",
            min_height="85vh",
            id='my-child'
        )
    
    return base_page(my_child)