# full_stack_python/contact/page.py

import reflex as rx 
import reflex_local_auth
from ..ui.base import base_page
from ..models import ContactEntryModel
from . import form
from .state import ContactEntryState, ContactAddFormState # Importamos ambos estados

def contact_entry_list_item(contact: ContactEntryModel) -> rx.Component:
    """Muestra una entrada de contacto individual en la lista."""
    return rx.box(
        rx.heading(f"{contact.first_name} ({contact.email})", size="4"),
        rx.text(contact.message, white_space="pre-wrap", margin_y="0.5em"),
        rx.text(f"Received on: {contact.created_at.strftime('%Y-%m-%d %H:%M')}", size="2", color_scheme="gray"),
        rx.cond(
            contact.userinfo_id,
            rx.text("Submitted by a logged-in user", size="2", weight="bold"),
            rx.text("Submitted by a guest", size="2", weight="bold"),
        ),
        padding="1em", border="1px solid", border_color=rx.color("gray", 6), border_radius="0.5em", width="100%"
    )

@reflex_local_auth.require_login
def contact_entries_list_page() -> rx.Component:
    """Página que muestra la lista de todas las entradas de contacto."""
    return base_page(
        rx.vstack(
            rx.heading("Contact History", size="7"),
            rx.foreach(
                # ¡CORRECCIÓN! Usa el estado correcto para la lista.
                ContactEntryState.entries,
                contact_entry_list_item
            ),
            spacing="5", align="center", width="100%", max_width="800px", margin="auto", min_height="85vh"
        )
    )

def contact_page() -> rx.Component:
    """La página principal de contacto con el formulario."""
    my_child = rx.vstack(
        rx.heading("Contact Us", size="9"),
        rx.cond(
            # ¡CORRECCIÓN! Usa el estado del formulario y su mensaje.
            ContactAddFormState.did_submit,
            rx.heading(ContactAddFormState.thank_you_message, size="5", text_align="center"),
            form.contact_form()
        ),
        spacing="5", justify="center", align="center", min_height="85vh",
    )
    return base_page(my_child)