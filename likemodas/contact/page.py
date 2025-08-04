import reflex as rx
import reflex_local_auth
from ..ui.base import base_page
from ..models import ContactEntryModel
from .form import contact_form
from .state import ContactState

def contact_entry_list_item(contact: ContactEntryModel) -> rx.Component:
    return rx.box(
        rx.heading(
            rx.cond(
                contact.email,
                f"{contact.first_name} ({contact.email})",
                f"{contact.first_name} (sin email)"
            ),
            size="4"
        ),
        rx.text(contact.message, white_space="pre-wrap", margin_y="0.5em"),
        rx.text(f"Recibido el: {contact.created_at_formatted}", size="2", color_scheme="gray"),
        rx.cond(
            contact.userinfo_id,
            rx.text("Enviado por un usuario registrado", size="2", weight="bold"),
            rx.text("Enviado por un invitado", size="2", weight="bold"),
        ),
        padding="1em",
        border="1px solid",
        border_color=rx.color("gray", 6),
        border_radius="0.5em",
        width="100%"
    )

@reflex_local_auth.require_login
def contact_entries_list_content() -> rx.Component:
    """Página que muestra la lista de todas las entradas."""
    return rx.vstack(
        rx.heading("Historial de Contacto", size="7"),
        rx.input(
            placeholder="Buscar en mensajes...",
            value=ContactState.search_query,
            on_change=ContactState.set_search_query,
            width="100%",
            max_width="400px",
            margin_y="1.5em",
        ),
        rx.foreach(ContactState.filtered_entries, contact_entry_list_item),
        spacing="5",
        align="center",
        width="100%",
        max_width="800px",
        margin="auto",
        min_height="85vh"
    )

def contact_page_content() -> rx.Component:
    """Página principal de contacto con formulario o mensaje de agradecimiento."""
    return rx.vstack(
        rx.heading("Contáctanos", size="9"),
        rx.cond(
            ContactState.did_submit,
            rx.heading(ContactState.thank_you_message, size="5", text_align="center"),
            contact_form()
        ),
        spacing="5",
        justify="center",
        align="center",
        min_height="85vh",
    )