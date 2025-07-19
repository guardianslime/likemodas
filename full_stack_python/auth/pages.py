import reflex as rx
import reflex_local_auth

from reflex_local_auth.pages.login import LoginState, login_form
from reflex_local_auth.pages.registration import RegistrationState, register_form

from .. import navigation
from ..ui.base import base_page, public_layout # ✨ 1. Importa public_layout

from .forms import my_register_form
from .state import SessionState
from .verify_state import VerifyState
from .forgot_password_state import ForgotPasswordState
from .reset_password_state import ResetPasswordState

def my_login_page() -> rx.Component:
    return base_page(
        rx.center(
            rx.cond(
                LoginState.is_hydrated,
                rx.card(
                    rx.vstack(
                        login_form(),
                        rx.link(
                            "¿Olvidaste tu contraseña?", 
                            href="/forgot-password", 
                            size="2", 
                            text_align="center",
                            margin_top="1em"
                        )
                    )
                ),
                rx.fragment()
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
    """Página para que el usuario verifique su correo."""
    page_content = rx.center(
        rx.vstack(
            rx.heading("Verificando tu cuenta...", size="8"),
            rx.text(VerifyState.message, text_align="center"),
            rx.spinner(size="3"), # Muestra un spinner mientras procesa
            spacing="5",
            padding="2em",
            border_radius="md",
            box_shadow="lg",
            bg=rx.color("gray", 2)
        ),
        min_height="85vh"
    )

    # ✨ 2. CAMBIO CRÍTICO: Usamos public_layout directamente, NO base_page.
    #    Esto evita el bloqueo de la lógica de verificación.
    return public_layout(page_content)

def forgot_password_page() -> rx.Component:
    return base_page(
        rx.center(
            rx.card(
                rx.form(
                    rx.vstack(
                        rx.heading("Recuperar Contraseña", size="7"),
                        rx.text("Introduce tu correo electrónico y te enviaremos un enlace para restablecer tu contraseña."),
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
                                color_scheme="green" if ForgotPasswordState.is_success else "red",
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
    return base_page(
        rx.center(
            rx.card(
                rx.cond(
                    ResetPasswordState.is_token_valid,
                    # Si el token es válido, muestra el formulario
                    rx.form(
                        rx.vstack(
                            rx.heading("Nueva Contraseña", size="7"),
                            rx.input(
                                placeholder="Nueva contraseña",
                                on_change=ResetPasswordState.set_password,
                                type="password",
                                width="100%"
                            ),
                            rx.input(
                                placeholder="Confirmar nueva contraseña",
                                on_change=ResetPasswordState.set_confirm_password,
                                type="password",
                                width="100%"
                            ),
                            rx.button("Guardar Contraseña", type="submit", width="100%"),
                            rx.cond(
                                ResetPasswordState.message,
                                rx.callout(
                                    ResetPasswordState.message,
                                    icon="alert_triangle",
                                    color_scheme="red",
                                    width="100%"
                                )
                            ),
                            spacing="4"
                        ),
                        on_submit=ResetPasswordState.handle_reset_password
                    ),
                    # Si el token no es válido, muestra el mensaje de error
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
        ),
        # El evento se ejecuta en cuanto carga la página para validar el token
        on_load=ResetPasswordState.on_load_check_token
    )