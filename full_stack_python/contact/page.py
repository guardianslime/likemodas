# full_stack_python/contact/page.py

import reflex as rx 
import reflex_local_auth
from ..ui.base import base_page
from ..models import ContactEntryModel
from .form import contact_form
# ¡CAMBIO CLAVE! Importamos los estados nuevos y separados
from .state import ContactHistoryState, ContactAddFormState

def contact_entry_list_item(contact: ContactEntryModel) -> rx.Component:
    """Muestra una entrada de contacto individual en la lista."""
    return rx.box(
        rx.heading(f"{contact.first_name} ({contact.email})", size="4"),
        rx.text(contact.message, white_space="pre-wrap", margin_y="0.5em"),
        rx.text(f"Recibido el: {contact.created_at_formatted}", size="2", color_scheme="gray"),
        rx.cond(
            contact.userinfo_id,
            rx.text("Enviado por un usuario registrado", size="2", weight="bold"),
            rx.text("Enviado por un invitado", size="2", weight="bold"),
        ),
        padding="1em", border="1px solid", border_color=rx.color("gray", 6), border_radius="0.5em", width="100%"
    )

@reflex_local_auth.require_login
def contact_entries_list_page() -> rx.Component:
    """
    Página que muestra la lista de todas las entradas.
    Sigue protegida por login, pero usa su propio estado para los datos.
    """
    return base_page(
        rx.vstack(
            rx.heading("Historial de Contacto", size="7"),
            # ¡CAMBIO CLAVE! Usa el nuevo estado de historial.
            rx.foreach(ContactHistoryState.entries, contact_entry_list_item),
            spacing="5", align="center", width="100%", max_width="800px", margin="auto", min_height="85vh"
        )
    )

def contact_page() -> rx.Component:
    """La página principal de contacto con el formulario."""
    return base_page(
        rx.vstack(
            rx.heading("Contáctanos", size="9"),
            rx.cond(
                ContactAddFormState.did_submit,
                rx.heading(ContactAddFormState.thank_you_message, size="5", text_align="center"),
                contact_form()
            ),
            spacing="5", justify="center", align="center", min_height="85vh",
        )
    )