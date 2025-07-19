import reflex as rx
import reflex_local_auth
from reflex_local_auth.pages.components import input_100w, MIN_WIDTH
from ..ui.password_input import password_input  # Importamos nuestro nuevo componente

from .state import MyRegisterState

def register_error() -> rx.Component:
    return rx.cond(
        reflex_local_auth.RegistrationState.error_message != "",
        rx.callout(
            # ✨ Añade rx.text con white_space="pre-wrap"
            rx.text(
                reflex_local_auth.RegistrationState.error_message, 
                white_space="pre-wrap"
            ),
            icon="triangle_alert",
            color_scheme="red",
            role="alert",
            width="100%",
        ),
    )

def my_register_form() -> rx.Component:
    """El formulario de registro, ahora con el input de contraseña personalizado."""
    return rx.form(
        rx.vstack(
            rx.heading("Create an account", size="7"),
            register_error(),
            rx.text("Username"),
            input_100w("username"),
            rx.text("Email"),
            input_100w("email", type='email'),
            rx.text("Password"),
            # ✨ CAMBIO: Usamos nuestro componente personalizado sin 'on_change'
            password_input(
                placeholder="Password",
                name="password"
            ),
            rx.text("Confirm password"),
            # ✨ CAMBIO: Usamos nuestro componente personalizado sin 'on_change'
            password_input(
                placeholder="Confirm password",
                name="confirm_password"
            ),
            rx.button("Sign up", width="100%"),
            rx.center(
                rx.link("Login", on_click=lambda: rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)),
                width="100%",
            ),
            min_width=MIN_WIDTH,
        ),
        on_submit=MyRegisterState.handle_registration_email,
    )

def login_error() -> rx.Component:
    """Muestra un error si el login falla."""
    return rx.cond(
        reflex_local_auth.LoginState.error_message != "",
        rx.callout(
            reflex_local_auth.LoginState.error_message,
            icon="triangle_alert",
            color_scheme="red",
            role="alert",
            width="100%",
        ),
    )

def my_login_form() -> rx.Component:
    """Un formulario de login personalizado con el input de contraseña visible."""
    return rx.form(
        rx.vstack(
            rx.heading("Login into your Account", size="7"),
            login_error(),
            rx.text("Username"),
            input_100w("username"),
            rx.text("Password"),
            # ✨ CAMBIO: Usamos nuestro componente personalizado
            password_input(
                placeholder="Password",
                on_change=reflex_local_auth.LoginState.set_password,
                name="password"
            ),
            rx.button("Sign in", width="100%"),
            rx.center(
                rx.link("Register", on_click=lambda: rx.redirect(reflex_local_auth.routes.REGISTER_ROUTE)),
                width="100%",
            ),
            min_width=MIN_WIDTH,
        ),
        on_submit=reflex_local_auth.LoginState.on_submit,
    )