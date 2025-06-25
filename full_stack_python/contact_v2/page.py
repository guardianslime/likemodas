# full_stack_python/contact_v2/page.py

import reflex as rx
import reflex_local_auth
from ..ui.base import base_page
from ..models import ContactEntryModel
from .state import ContactV2State
from .form import contact_v2_form  # <-- ARREGLO FINAL: de .forms a .form

def entry_list_item(entry: ContactEntryModel):
    """Muestra un item individual de la lista de entradas."""
    return rx.box(
        rx.heading(entry.first_name, size="5"),
        rx.text(entry.message),
        rx.text(f"Enviado el: {entry.created_at.strftime('%Y-%m-%d %H:%M')}", size="2", color_scheme="gray"),
        border="1px solid #ddd",
        padding="1em",
        border_radius="8px",
        width="100%",
    )

@reflex_local_auth.require_login
def contact_v2_list_page() -> rx.Component:
    """Página que muestra las entradas enviadas por el usuario."""
    return base_page(
        rx.vstack(
            rx.heading("Mis Mensajes Enviados", size="7"),
            rx.link(rx.button("Enviar Nuevo Mensaje"), href="/contact-v2/add"),
            rx.cond(
                ContactV2State.entries,
                rx.vstack(
                    rx.foreach(ContactV2State.entries, entry_list_item),
                    spacing="4",
                    width="100%",
                ),
                rx.box(
                    rx.text("Aún no has enviado ningún mensaje."),
                    padding_top="2em",
                )
            ),
            spacing="5",
            align="center",
            min_height="85vh",
            width=["90%", "80%", "60%"],
            margin="auto",
        )
    )

@reflex_local_auth.require_login
def contact_v2_add_page() -> rx.Component:
    """Página para enviar un nuevo mensaje."""
    return base_page(
        rx.vstack(
            rx.heading("Enviar un Nuevo Mensaje", size="7"),
            contact_v2_form(),
            spacing="5",
            align="center",
            min_height="85vh",
            width=["90%", "80%", "50%"],
            margin="auto",
        )
    )