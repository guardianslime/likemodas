# full_stack_python/contact/page.py
import reflex as rx 
from ..ui.base import base_page
from ..models import ContactEntryModel
from . import form, state

def contact_entry_list_item(contact: ContactEntryModel):
    """Muestra una entrada de contacto individual en la lista."""
    return rx.box(
        rx.hstack(
            rx.heading(contact.first_name, size="3"),
            rx.text(contact.last_name or ""),
            spacing="2",
        ),
        rx.text(contact.email or "No email provided"),
        rx.text("Message:", contact.message),
        padding="1em",
        border_width="1px",
        border_radius="md",
        width="100%",
    )

def contact_entries_list_page() -> rx.Component:
    """Página que lista todas las entradas de contacto."""
    return base_page(
        rx.vstack(
            rx.heading("Contact Entries", size="7"),
            rx.text("Messages submitted through the contact form."),
            # ¡CORRECCIÓN CLAVE! Este rx.cond ahora funcionará.
            rx.cond(
                state.ContactState.entries,
                # Si la lista NO está vacía, la muestra.
                rx.vstack(
                    rx.foreach(
                        state.ContactState.entries,
                        contact_entry_list_item,
                    ),
                    spacing="4",
                    width="100%",
                ),
                # Si la lista ESTÁ vacía, muestra este mensaje.
                rx.box(
                    rx.text("No contact entries have been submitted yet."),
                    padding_y="2em",
                )
            ),
            spacing="4",
            align="center",
            width=["90vw", "80vw", "60vw"],
        ),
        on_load=state.ContactState.list_entries,
    )

def contact_page() -> rx.Component:
    """Página con el formulario de contacto."""
    return base_page(
        rx.vstack(
            rx.heading("Contact Us", size="9"),
            rx.cond(
                state.ContactState.did_submit,
                rx.box(
                    rx.icon("check_circle", size=32, color="green"),
                    rx.text(state.ContactState.thank_you),
                    padding="1em",
                    border="1px solid green",
                    border_radius="md",
                ),
                form.contact_form(),
            ),
            spacing="5",
            justify="center",
            align="center",
            min_height="85vh",
            width="100%",
        )
    )