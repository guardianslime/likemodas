# full_stack_python/contact/form.py

import reflex as rx 
from ..auth.state import SessionState
# ¡CORRECCIÓN! Se elimina la importación de 'ContactState' de la parte superior del archivo.
# from .state import ContactState

def contact_form() -> rx.Component:
    # ¡CORRECCIÓN! Se importa 'ContactState' DENTRO de la función que la necesita.
    from .state import ContactState

    return rx.form(
            rx.vstack(
                rx.hstack(
                    rx.input(
                        name="first_name",
                        placeholder="first name",
                        required=False,
                        type= "text",
                        width="100%",
                    ),
                    rx.input(
                        name="last_name",
                        placeholder="Last Name",
                        type="text",
                        width="100%",
                    ),
                    width="100%",
                ),
                rx.input(
                    name= "email",
                    placeholder="Your email",
                    type= "email",
                    width="100%",
                ), 
                rx.text_area(
                    name="message",
                    placeholder="Your message",
                    required=True,
                    width='100%',
                ),
                rx.button("Submit", type="submit"),
            ),
            on_submit=ContactState.handle_submit,
            reset_on_submit=True,
    )