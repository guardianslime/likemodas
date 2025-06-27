# full_stack_python/contact/form.py
import reflex as rx
from .state import ContactAddFormState # Importa el estado correcto

def contact_form() -> rx.Component:
    """El formulario para crear una nueva entrada de contacto."""
    return rx.form(
        rx.vstack(
            rx.hstack(
                rx.input(name="first_name", placeholder="Nombre", width="100%"),
                rx.input(name="last_name", placeholder="Apellido", width="100%"),
                width="100%",
            ),
            rx.input(name="email", placeholder="Tu Email", type="email", width="100%"), 
            rx.text_area(name="message", placeholder="Tu mensaje", required=True, width='100%'),
            rx.button("Enviar", type="submit"),
        ),
        on_submit=ContactAddFormState.handle_submit, # Usa el manejador del estado dedicado
        reset_on_submit=True,
    )