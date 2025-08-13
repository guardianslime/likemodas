import reflex as rx
from ..ui.base import base_page

def my_account_redirect_content() -> rx.Component:
    """Página de carga para la sección 'Mi Cuenta'."""
    return rx.center(
        rx.vstack(
            rx.spinner(size="3"),
            rx.text("Redirigiendo a tu cuenta..."),
            spacing="4"
        ),
        min_height="85vh"
    )
