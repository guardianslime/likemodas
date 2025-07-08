import reflex as rx
from .state import ContactState

def contact_form() -> rx.Component:
    """Formulario para enviar un mensaje de contacto."""
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
        on_submit=ContactState.handle_submit,
        reset_on_submit=True,
    )
