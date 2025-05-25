import reflex as rx

from reflex_local_auth.pages.login import LoginState, login_form, PADDING_TOP

from ..ui.base import base_page

def my_login_page()->rx.Component:

    return base_page(
        rx.center(
            rx.cond(
                LoginState.is_hydrated, # type: ignore
                rx.card(login_form()),
            ),
             min_height="85vh",
            padding_top=PADDING_TOP,           
        ),

    )