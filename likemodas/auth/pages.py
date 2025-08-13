# likemodas/auth/pages.py (CORREGIDO)

import reflex as rx
import reflex_local_auth
from reflex_local_auth.pages.components import input_100w, MIN_WIDTH
from ..ui.password_input import password_input
from .forms import my_register_form
from ..state import AppState

def my_login_page_content() -> rx.Component:
    return rx.center(
        rx.card(
            rx.vstack(
                rx.form(
                    rx.vstack(
                        rx.heading("Inicia Sesión en tu Cuenta", size="7"),
                        rx.cond(
                            reflex_local_auth.LoginState.error_message != "",
                            rx.callout(
                                reflex_local_auth.LoginState.error_message,
                                icon="triangle_alert", color_scheme="red", role="alert", width="100%"
                            ),
                        ),
                        rx.text("Nombre de usuario"),
                        input_100w("username"),
                        rx.text("Contraseña"),
                        password_input(
                            placeholder="Password",
                            name="password"
                        ),
                        rx.button("Iniciar Sesión", width="100%", type="submit"),
                        spacing="4"
                    ),
                    on_submit=reflex_local_auth.LoginState.on_submit
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

def my_register_page_content() -> rx.Component:
    """Página de registro que muestra éxito o el formulario desde AppState."""
    return rx.center(
        rx.cond(
            AppState.success,
            rx.vstack(
                rx.heading("¡Registro Exitoso!", size="7"),
                rx.text("Revisa tu correo electrónico para verificar tu cuenta."),
                rx.link(rx.button("Ir a Iniciar Sesión"), href=reflex_local_auth.routes.LOGIN_ROUTE)
            ),
            rx.card(my_register_form()),
        ),
        min_height="85vh",
    )

def verification_page_content() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading("Verificando tu cuenta...", size="8"),
            # ✨ CORRECCIÓN: Se usa info_message en lugar de message
            rx.text(AppState.info_message, text_align="center"),
            rx.spinner(size="3"),
            spacing="5", padding="2em",
        ),
        min_height="85vh"
    )

def forgot_password_page_content() -> rx.Component:
    return rx.center(
        rx.card(
            rx.form(
                rx.vstack(
                    rx.heading("Recuperar Contraseña", size="7"),
                    rx.text("Introduce tu correo y te enviaremos un enlace."),
                    rx.input(placeholder="Email", name="email", type="email", width="100%"),
                    rx.button("Enviar Enlace", type="submit", width="100%"),
                    rx.cond(
                        AppState.info_message,
                        rx.callout(
                            # ✨ CORRECCIÓN: Se usa info_message en lugar de message
                            AppState.info_message,
                            icon="info",
                            color_scheme=rx.cond(AppState.is_success, "green", "red"),
                            width="100%"
                        )
                    ),
                    spacing="4"
                ),
                on_submit=AppState.handle_forgot_password
            )
        ),
        min_height="85vh"
    )

def reset_password_page_content() -> rx.Component:
    return rx.center(
        rx.card(
            rx.cond(
                AppState.is_token_valid,
                rx.form(
                    rx.vstack(
                        rx.heading("Nueva Contraseña", size="7"),
                        password_input(placeholder="Nueva contraseña", name="password"),
                        password_input(placeholder="Confirmar nueva contraseña", name="confirm_password"),
                        rx.button("Guardar Contraseña", type="submit", width="100%"),
                        rx.cond(
                            AppState.info_message,
                            rx.callout(
                                # ✨ CORRECCIÓN: Se usa info_message en lugar de message
                                rx.text(AppState.info_message, white_space="pre-wrap"),
                                icon="triangle_alert", color_scheme="red", width="100%"
                            )
                        ),
                        spacing="4"
                    ),
                    on_submit=AppState.handle_reset_password
                ),
                rx.vstack(
                    rx.heading("Enlace no válido", size="7"),
                    # ✨ CORRECCIÓN: Se usa info_message en lugar de message
                    rx.text(AppState.info_message),
                    rx.link("Solicitar un nuevo enlace", href="/forgot-password"),
                    spacing="4", align="center"
                )
            )
        ),
        min_height="85vh"
    )