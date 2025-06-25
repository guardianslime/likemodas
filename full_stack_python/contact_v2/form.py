# full_stack_python/contact_v2/forms.py

import reflex as rx
from .state import ContactV2FormState

def contact_v2_form() -> rx.Component:
    """
    Define el nuevo formulario de contacto, copiando la estructura del formulario del blog.
    """
    return rx.form(
        rx.vstack(
            rx.input(
                name="first_name",
                placeholder="Tu Nombre",
                required=True,
                width="100%",
            ),
            rx.text_area(
                name="message",
                placeholder="Tu Mensaje",
                required=True,
                height="200px",
                width="100%",
            ),
            rx.button("Enviar Mensaje", type="submit", width="100%"),
        ),
        on_submit=ContactV2FormState.handle_submit,
        reset_on_submit=True,
        width="100%",
    )