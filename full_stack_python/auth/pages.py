import reflex as rx

from reflex_local_auth.pages.login import LoginState, login_form
from reflex_local_auth.pages.registration import RegistrationState, register_form

from .. import navigation
from ..ui.base import base_page

from .forms import my_register_form
from .state import SessionState
from .verify_state import VerifyState

def my_login_page() -> rx.Component:
    return base_page(
        rx.center(
            rx.cond(
                LoginState.is_hydrated,
                rx.card(login_form()),
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
    return base_page(
        rx.center(
            rx.vstack(
                rx.heading("Verificación de Correo", size="8"),
                rx.text(VerifyState.message, text_align="center"),
                rx.cond(
                    VerifyState.is_verified,
                    rx.link(
                        rx.button("Ir a Iniciar Sesión"),
                        href=reflex_local_auth.routes.LOGIN_ROUTE,
                        margin_top="1em"
                    )
                ),
                spacing="5",
                padding="2em",
                border_radius="md",
                box_shadow="lg",
                bg=rx.color("gray", 2)
            ),
            min_height="85vh"
        ),
        on_load=VerifyState.verify_token
    )