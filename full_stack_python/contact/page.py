# full_stack_python/contact/page.py
import reflex as rx
from .state import ContactState
from ..ui.base import base
from .. import navigation
from ..auth.state import AuthState

def contact_form() -> rx.Component:
    """El componente del formulario de contacto."""
    return rx.form.root(
        rx.vstack(
            rx.form.field(
                rx.form.label("Nombre"),
                rx.form.control(
                    rx.input(placeholder="Introduce tu nombre", name="name"),
                ),
                name="name",
            ),
            rx.form.field(
                rx.form.label("Email"),
                rx.form.control(
                    rx.input(placeholder="Introduce tu email", name="email", type="email"),
                ),
                name="email",
            ),
            rx.form.field(
                rx.form.label("Mensaje"),
                rx.form.control(
                    rx.text_area(placeholder="Escribe tu mensaje", name="message"),
                ),
                name="message",
            ),
            rx.form.submit(rx.button("Enviar", type="submit")),
            width="100%",
        ),
        on_submit=ContactState.handle_submit,
        reset_on_submit=True,
    )

def thank_you_message() -> rx.Component:
    """El componente de mensaje de agradecimiento."""
    return rx.vstack(
        rx.heading("¡Gracias!", size="5"),
        rx.text("Tu mensaje ha sido enviado correctamente."),
        rx.button(
            "Enviar otro mensaje",
            on_click=ContactState.reset_form,
            margin_top="1rem",
        ),
        align="center",
        spacing="3",
        padding_y="2rem",
    )

@rx.page(route=navigation.routes.CONTACT_US, on_load=AuthState.check_login)
def contact_page() -> rx.Component:
    """La página de contacto. El usuario debe estar logueado."""
    return base(
        rx.vstack(
            rx.heading("Contáctanos", size="7", margin_bottom="1rem"),
            rx.cond(
                AuthState.is_logged_in,
                rx.box(
                    rx.cond(
                        ContactState.submitted,
                        thank_you_message(),
                        contact_form(),
                    ),
                    width="100%",
                    max_width="600px",
                    margin_top="2rem",
                ),
                rx.vstack(
                    rx.text("Redirigiendo a la página de inicio de sesión..."),
                    rx.spinner(),
                    align="center",
                )
            ),
            align="center",
            width="100%",
            padding_x="1rem",
        )
    )

def contact_entries_table() -> rx.Component:
    """Una tabla con las entradas del formulario."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Nombre"),
                rx.table.column_header_cell("Email"),
                rx.table.column_header_cell("Mensaje"),
                rx.table.column_header_cell("Enviado por"),
            )
        ),
        rx.table.body(
            rx.foreach(
                ContactState.entries,
                lambda entry: rx.table.row(
                    rx.table.cell(entry.name),
                    rx.table.cell(entry.email),
                    rx.table.cell(entry.message),
                    rx.table.cell(
                        rx.cond(
                            entry.user,
                            entry.user.username,
                            "Invitado"
                        )
                    ),
                ),
            )
        ),
    )

@rx.page(route=navigation.routes.CONTACT_ENTRIES, on_load=[ContactState.load_entries, AuthState.check_login])
def contact_entries() -> rx.Component:
    """La página de entradas del formulario. El usuario debe estar logueado."""
    return base(
        rx.vstack(
            rx.cond(
                AuthState.is_logged_in,
                 rx.vstack(
                    rx.heading("Entradas de Contacto", size="7", margin_bottom="1rem"),
                    contact_entries_table(),
                    align="center",
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Redirigiendo a la página de inicio de sesión..."),
                    rx.spinner(),
                    align="center",
                )
            ),
            width="100%",
            padding_x="1rem",
        )
    )