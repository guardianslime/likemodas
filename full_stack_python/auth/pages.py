import reflex as rx
import reflex_local_auth

from reflex_local_auth.pages.login import LoginState
from reflex_local_auth.pages.registration import RegistrationState

from .. import navigation
from ..ui.base import base_page, public_layout

from .forms import my_register_form
from .state import SessionState
from .verify_state import VerifyState
from .forgot_password_state import ForgotPasswordState
from .reset_password_state import ResetPasswordState

# --- Lógica para el icono de mostrar/ocultar contraseña ---

class PasswordState(rx.State):
    """Estado para manejar la visibilidad de un campo de contraseña."""
    show_password: bool = False

    def toggle_visibility(self):
        self.show_password = ~self.show_password

def _password_input(placeholder: str, name: str, on_change: rx.EventChain = None) -> rx.Component:
    """
    Un componente local de input de contraseña con un icono para mostrar/ocultar.
    on_change ahora es opcional.
    """
    return rx.box(
        rx.input(
            placeholder=placeholder,
            name=name,
            on_change=on_change,
            type=rx.cond(PasswordState.show_password, "text", "password"),
            width="100%",
            pr="2.5em",
        ),
        rx.box(
            rx.icon(
                tag=rx.cond(PasswordState.show_password, "eye_off", "eye"),
                on_click=PasswordState.toggle_visibility,
                cursor="pointer",
                color=rx.color("gray", 10),
            ),
            position="absolute",
            right="0.75em",
            top="50%",
            transform="translateY(-50%)",
        ),
        position="relative",
        width="100%",
    )

# --- Fin de la lógica del icono ---

def my_login_page() -> rx.Component:
    """Página de login que ahora usa nuestro campo de contraseña con icono."""
    return base_page(
        rx.center(
            rx.card(
                rx.vstack(
                    rx.form(
                        rx.vstack(
                            rx.heading("Login into your Account", size="7"),
                            rx.text("Username"),
                            rx.input(
                                placeholder="Username",
                                name="username", # El nombre es importante para el submit
                                on_change=LoginState.set_username, 
                                width="100%"
                            ),
                            rx.text("Password"),
                            # ✨ CAMBIO: Eliminamos on_change y pasamos el 'name'
                            _password_input(
                                placeholder="Password",
                                name="password",
                            ),
                            rx.button("Sign in", width="100%", type="submit"),
                            spacing="4"
                        ),
                        on_submit=LoginState.on_submit
                    ),
                    rx.link(
                        "¿Olvidaste tu contraseña?", 
                        href="/forgot-password", 
                        size="2", 
                        text_align="center",
                        margin_top="1em"
                    )
                )
            ),
            min_height="85vh",
        )
    )

# ... (El resto de las funciones de página se quedan igual que en tu archivo)
def my_register_page() -> rx.Component:
    # ... (sin cambios)
    return base_page(...)

def my_logout_page() -> rx.Component:
    # ... (sin cambios)
    return base_page(...)

def verification_page() -> rx.Component:
    # ... (sin cambios)
    page_content = rx.center(...)
    return public_layout(page_content)

def forgot_password_page() -> rx.Component:
    # ... (sin cambios)
    return base_page(...)

def reset_password_page() -> rx.Component:
    """Página de reseteo que ahora usa nuestro campo de contraseña con icono."""
    page_content = rx.center(
        rx.card(
            rx.cond(
                ResetPasswordState.is_token_valid,
                rx.form(
                    rx.vstack(
                        rx.heading("Nueva Contraseña", size="7"),
                        _password_input(
                            placeholder="Nueva contraseña",
                            name="password", # Pasamos el nombre
                            on_change=ResetPasswordState.set_password,
                        ),
                        _password_input(
                            placeholder="Confirmar nueva contraseña",
                            name="confirm_password", # Pasamos el nombre
                            on_change=ResetPasswordState.set_confirm_password,
                        ),
                        rx.button("Guardar Contraseña", type="submit", width="100%"),
                        rx.cond(
                            ResetPasswordState.message,
                            rx.callout(
                                ResetPasswordState.message,
                                icon="triangle_alert",
                                color_scheme="red",
                                width="100%"
                            )
                        ),
                        spacing="4"
                    ),
                    on_submit=ResetPasswordState.handle_reset_password
                ),
                rx.vstack(
                    rx.heading("Enlace no válido", size="7"),
                    rx.text(ResetPasswordState.message),
                    rx.link("Solicitar un nuevo enlace", href="/forgot-password"),
                    spacing="4",
                    align="center"
                )
            )
        ),
        min_height="85vh"
    )
    return public_layout(page_content)