# full_stack_python/contact/page.py

import reflex as rx
from full_stack_python.navigation import Route
from full_stack_python.ui.base import base
from .form import contact_form
from .state import AuthState, ContactState


def list_contact_entries():
    """List the contact entries."""
    return rx.vstack(
        rx.heading("Contact Entries", size="5"),
        rx.data_table(
            data=ContactState.contact_entries,
            columns=["name", "email", "message", "created_at"],
        ),
        align="center",
    )


@rx.page(
    route=Route.CONTACT_ENTRIES.value,
    # --- CORRECCIÓN LÓGICA AQUÍ ---
    # Se asegura de verificar el login antes de cargar las entradas.
    on_load=[ContactState.check_login, ContactState.load_entries],
)
def contact_entries_page() -> rx.Component:
    """The contact entries page."""
    return base(
        rx.vstack(
            rx.cond(
                ContactState.logged_in,
                list_contact_entries(),
                rx.text("You must be logged in to view entries."),
            ),
            align="center",
        )
    )


@rx.page(route=Route.CONTACT.value, on_load=AuthState.check_login)
def contact_page() -> rx.Component:
    """The contact page."""
    return base(
        rx.vstack(
            rx.heading("Contact Us", size="9"),
            contact_form(),
            align="center",
            spacing="7",
        )
    )