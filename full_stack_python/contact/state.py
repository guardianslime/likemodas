# full_stack_python/contact/page.py

import reflex as rx 
import reflex_local_auth
from ..ui.base import base_page
from ..models import ContactEntryModel
from . import form, state

def contact_entry_list_item(contact: ContactEntryModel):
    """Muestra una entrada de contacto individual de forma más clara."""
    return rx.box(
        rx.heading(f"{contact.first_name} ({contact.email})", size="4"),
        rx.text(contact.message, white_space="pre-wrap", margin_y="0.5em"),
        rx.text(f"Received on: {contact.created_at.strftime('%Y-%m-%d %H:%M')}", size="2", color_scheme="gray"),
        rx.cond(
            contact.userinfo_id,
            rx.text("Submitted by logged-in user", size="2", weight="bold"),
            rx.text("Submitted by a guest", size="2", weight="bold"),
        ),
        padding="1em",
        border="1px solid",
        border_color=rx.color("gray", 6),
        border_radius="0.5em",
        width="100%"
    )

@reflex_local_auth.require_login
def contact_entries_list_page() -> rx.Component:
    """Página que muestra la lista de entradas de contacto."""
    return base_page(
        rx.vstack(
            rx.heading("Contact Entries", size="7"),
            rx.foreach(
                state.ContactState.entries,
                contact_entry_list_item
            ),
            spacing="5",
            align="center",
            width="100%",
            max_width="800px",
            margin="auto",
            min_height="85vh",
        )
    )

def contact_page() -> rx.Component:
    """
    Página de contacto que muestra un mensaje de agradecimiento o el formulario,
    manteniendo el diseño responsivo.
    """
    # ¡CORRECCIÓN! Aquí se soluciona el ValueError.
    # Se define un componente condicional que envuelve la variable 'thank_you' en un rx.heading.
    thank_you_or_form = rx.cond(
        state.ContactState.did_submit,
        rx.heading(state.ContactState.thank_you, size="5", text_align="center"),
        form.contact_form()
    )

    my_child = rx.vstack(
            rx.heading("Contact us", size="9"),
            
            # Se usa el componente condicional en cada vista responsiva.
            rx.desktop_only(
                rx.box(
                    thank_you_or_form,
                    width="50vw"
                )
            ),
            rx.tablet_only(
                rx.box(
                    thank_you_or_form,
                    width="75vw"
                )
            ),
            rx.mobile_only(
                rx.box(
                    thank_you_or_form,
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