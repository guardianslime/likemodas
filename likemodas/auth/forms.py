# likemodas/auth/forms.py (CORREGIDO)

import reflex as rx
import reflex_local_auth
from reflex_local_auth.pages.components import input_100w, MIN_WIDTH
from ..ui.password_input import password_input
from ..state import AppState  # Asegúrate de que AppState está importado

def register_error() -> rx.Component:
    """Muestra errores de registro."""
    return rx.cond(
        # ✅ CAMBIO: Apuntar a la variable de error de nuestro AppState
        AppState.error_message != "",
        rx.callout(
            rx.text(
                # ✅ CAMBIO: Mostrar el mensaje de error de nuestro AppState
                AppState.error_message,
                white_space="pre-wrap"
            ),
            icon="triangle_alert",
            color_scheme="red",
            role="alert",
            width="100%",
        ),
    )

def my_register_form() -> rx.Component:
    """El formulario de registro, ahora usando AppState."""
    return rx.form(
        rx.vstack(
            rx.heading("Create an account", size="7"),
            register_error(),
            rx.text("Username"),
            input_100w("username"),
            rx.text("Email"),
            input_100w("email", type='email'),
            rx.text("Password"),
            password_input(placeholder="Password", name="password"),
            rx.text("Confirm password"),
            password_input(placeholder="Confirm password", name="confirm_password"),
            rx.button("Sign up", width="100%"),
            rx.center(
                rx.link("Login", on_click=lambda: rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)),
                width="100%",
            ),
            min_width=MIN_WIDTH,
        ),
        # CAMBIO CLAVE: on_submit ahora llama al método correcto en AppState.
        on_submit=AppState.handle_registration_email,
    )