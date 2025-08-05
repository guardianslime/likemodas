# likemodas/contact/page.py (CORREGIDO Y COMPLETO)

import reflex as rx
import reflex_local_auth
from ..models import ContactEntryModel
from ..state import AppState

def contact_form() -> rx.Component:
    """Formulario para enviar un mensaje de contacto, usando AppState."""
    return rx.form(
        rx.vstack(
            rx.hstack(
                rx.input(name="first_name", placeholder="Nombre", width="100%", required=True),
                rx.input(name="last_name", placeholder="Apellido", width="100%"),
                width="100%",
            ),
            rx.input(name="email", placeholder="Tu Email", type="email", width="100%", required=True),
            rx.text_area(name="message", placeholder="Tu mensaje", required=True, width="100%"),
            rx.button("Enviar", type="submit"),
        ),
        # CAMBIO CLAVE: El on_submit ahora apunta al método en AppState.
        on_submit=AppState.handle_contact_submit,
        reset_on_submit=True,
    )

def contact_entry_list_item(contact: ContactEntryModel) -> rx.Component:
    """Muestra un mensaje de contacto individual."""
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
    """Página que muestra la lista de todas las entradas de contacto."""
    return rx.vstack(
        rx.heading("Historial de Contacto", size="7"),
        rx.input(
            placeholder="Buscar en mensajes...",
            # CAMBIO CLAVE: Todas las referencias de estado apuntan a AppState.
            value=AppState.search_query_contact,
            on_change=AppState.set_search_query_contact,
            width="100%",
            max_width="400px",
            margin_y="1.5em",
        ),
        rx.foreach(AppState.filtered_entries, contact_entry_list_item),
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
            # CAMBIO CLAVE: Se usa la variable de estado de AppState.
            AppState.did_submit_contact,
            rx.heading(AppState.thank_you_message, size="5", text_align="center"),
            contact_form()
        ),
        spacing="5",
        justify="center",
        align="center",
        min_height="85vh",
    )