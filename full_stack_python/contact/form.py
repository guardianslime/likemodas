# full_stack_python/contact/form.py

import reflex as rx 
from .state import ContactAddFormState

def contact_form() -> rx.Component:
    """El formulario para crear una nueva entrada de contacto."""
    return rx.form(
        rx.vstack(
            rx.hstack(
                rx.input(name="first_name", placeholder="First Name", width="100%"),
                rx.input(name="last_name", placeholder="Last Name", width="100%"),
                width="100%",
            ),
            rx.input(name="email", placeholder="Your Email", type="email", width="100%"), 
            rx.text_area(name="message", placeholder="Your message", required=True, width='100%'),
            rx.button("Submit", type="submit"),
        ),
        # ¡CORRECCIÓN! Ahora usa el estado dedicado para el formulario.
        on_submit=ContactAddFormState.handle_submit,
        reset_on_submit=True,
    )