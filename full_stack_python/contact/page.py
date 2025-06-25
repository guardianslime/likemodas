# full_stack_python/contact/page.py

import reflex as rx 
from ..ui.base import base_page
from ..models import ContactEntryModel
from . import form, state

def contact_entry_list_item(contact: ContactEntryModel):
    """
    Muestra una entrada de contacto individual.
    """
    return rx.box(
        rx.heading(contact.first_name),
        rx.text("Messages:", contact.message),
        rx.cond(
            contact.userinfo_id,
            rx.text("User associated, ID:", f"{contact.userinfo_id}"),
            rx.fragment("")
        ),
        padding="1em"
    )

def contact_entries_list_page() -> rx.Component:
    
    return base_page(
        rx.vstack(
            rx.heading("Contact Entries", size="5"),
            rx.cond(
                state.ContactState.entries,
                rx.foreach(
                    state.ContactState.entries,
                    contact_entry_list_item
                ),
                # Si la lista está vacía, muestra este mensaje
                rx.box(
                    rx.text("No contact entries have been submitted yet for your account."),
                    padding_top="2em"
                )
            ),
            spacing="5",
            align="center",
            min_height="85vh",
        ),
        # --- ARREGLO PRINCIPAL AQUÍ ---
        # Primero se verifica el login y luego se listan las entradas
        on_load=[state.ContactState.check_login, state.ContactState.list_entries]
    )

def contact_page() -> rx.Component:
    """
    Página con el formulario de contacto.
    """
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
    
    # Esta página necesita también el check_login para que el envío asocie al usuario
    return base_page(my_child, on_load=state.ContactState.check_login)