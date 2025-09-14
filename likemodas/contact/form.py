# likemodas/contact/form.py (CORREGIDO Y COMPLETO)

import reflex as rx
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
            rx.button("Enviar", type="submit", color_scheme="violet"),
        ),
        # CAMBIO CLAVE: El on_submit ahora apunta al método en AppState.
        on_submit=AppState.handle_contact_submit,
        reset_on_submit=True,
    )
