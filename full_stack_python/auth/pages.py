import reflex as rx
import reflex_local_auth

from reflex_local_auth.pages.login import LoginState
from reflex_local_auth.pages.registration import RegistrationState

from .. import navigation
from ..ui.base import base_page, public_layout

# Importamos los formularios y estados necesarios
from .forms import my_register_form
from .state import SessionState
from .verify_state import VerifyState
from .forgot_password_state import ForgotPasswordState
from .reset_password_state import ResetPasswordState

# --- Lógica para el icono de mostrar/ocultar contraseña ---
class PasswordState(rx.State):
    show_password: bool = False
    def toggle_visibility(self):
        self.show_password = ~self.show_password

def _password_input(placeholder: str, name: str, on_change: rx.EventChain = None) -> rx.Component:
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
                                name="username",
                                width="100%"
                            ),
                            rx.text("Password"),
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

def my_register_page() -> rx.Component:
    return base_page(
        rx.center(
            rx.cond(
                RegistrationState.success,
                rx.vstack(
                    rx.text("Registration successful!"),
                ),
                rx.card(my_register_form()),
            ),
            min_height="85vh",
        )
    )

def my_logout_page() -> rx.Component:
    # ✨ CÓDIGO COMPLETO RESTAURADO AQUÍ
    return base_page(
        rx.vstack(
            rx.heading("Are you sure you want to logout?", size="7"),
            rx.link(
                rx.button("No", color_scheme="gray"),
                href=navigation.routes.HOME_ROUTE
            ),
            rx.button("Yes, please logout", on_click=SessionState.perform_logout),
            spacing="5",
            justify="center",
            align="center",
            text_align="center",
            min_height="85vh",
            id="my-child"
        )
    )

def verification_page() -> rx.Component:
    # ✨ CÓDIGO COMPLETO RESTAURADO AQUÍ
    page_content = rx.center(
        rx.vstack(
            rx.heading("Verificando tu cuenta...", size="8"),
            rx.text(VerifyState.message, text_align="center"),
            rx.spinner(size="3"),
            spacing="5",
            padding="2em",
            border_radius="md",
            box_shadow="lg",
            bg=rx.color("gray", 2)
        ),
        min_height="85vh"
    )
    return public_layout(page_content)

def forgot_password_page() -> rx.Component:
    # ✨ CÓDIGO COMPLETO RESTAURADO AQUÍ
    return base_page(
        rx.center(
            rx.card(
                rx.form(
                    rx.vstack(
                        rx.heading("Recuperar Contraseña", size="7"),
                        rx.text("Introduce tu correo y te enviaremos un enlace."),
                        rx.input(
                            placeholder="Email",
                            on_change=ForgotPasswordState.set_email,
                            type="email",
                            width="100%"
                        ),
                        rx.button("Enviar Enlace", type="submit", width="100%"),
                        rx.cond(
                            ForgotPasswordState.message,
                            rx.callout(
                                ForgotPasswordState.message,
                                icon="info",
                                color_scheme=rx.cond(ForgotPasswordState.is_success, "green", "red"),
                                width="100%"
                            )
                        ),
                        spacing="4"
                    ),
                    on_submit=ForgotPasswordState.handle_submit
                )
            ),
            min_height="85vh"
        )
    )

def reset_password_page() -> rx.Component:
    page_content = rx.center(
        rx.card(
            rx.cond(
                ResetPasswordState.is_token_valid,
                rx.form(
                    rx.vstack(
                        rx.heading("Nueva Contraseña", size="7"),
                        _password_input(
                            placeholder="Nueva contraseña",
                            name="password",
                            on_change=ResetPasswordState.set_password,
                        ),
                        _password_input(
                            placeholder="Confirmar nueva contraseña",
                            name="confirm_password",
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