import reflex as rx
from ..state import AppState

def tfa_verify_page_content() -> rx.Component:
    return rx.center(
        rx.card(
            rx.form(
                rx.vstack(
                    rx.heading("Verificación Requerida", size="7"),
                    rx.text("Abre tu aplicación de autenticación e introduce el código."),
                    rx.input(name="tfa_code", placeholder="123456", required=True, max_length=6, style={"text_align": "center"}),
                    rx.button("Verificar", type="submit", width="100%"),
                    spacing="4",
                ),
                on_submit=AppState.verify_tfa_login,
            ),
        ),
        min_height="85vh",
    )