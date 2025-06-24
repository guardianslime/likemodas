# guardianslime/full-stack-python/full-stack-python-8c473aa59b63fc9e7a7075ae9cbea38efb6553ed/full_stack_python/contact/page.py

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
        # Verifica si la entrada de contacto está asociada a un usuario.
        rx.cond(
            contact.userinfo_id,
            rx.text("User associated, ID:", f"{contact.userinfo_id}"),
            rx.fragment("")  # No muestra nada si no hay un usuario asociado.
        ),
        padding="1em"
    )

def contact_entries_list_page() -> rx.Component:
    # La corrección principal está aquí: se añade el evento on_load.
    # Esto le dice a la página que ejecute ContactState.list_entries
    # tan pronto como la página se cargue en el navegador.
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
        ),
        on_load=state.ContactState.list_entries  # <-- ¡ESTA ES LA LÍNEA CLAVE DE LA CORRECCIÓN!
    )

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