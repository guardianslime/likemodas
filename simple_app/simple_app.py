"""El archivo principal de la aplicación."""

import reflex as rx
from .state import State

def index() -> rx.Component:
    """La página principal de la aplicación."""
    return rx.center(
        rx.vstack(
            rx.heading("Bienvenido a Reflex!", size="9"),
            rx.heading("Contador Simple", size="7"),
            rx.hstack(
                rx.button(
                    "Restar",
                    on_click=State.decrement,
                    color_scheme="red",
                    size="3",
                ),
                rx.heading(State.count, size="9"),
                rx.button(
                    "Sumar",
                    on_click=State.increment,
                    color_scheme="green",
                    size="3",
                ),
                spacing="5",
                align="center",
            ),
            spacing="7",
            align="center",
        ),
        min_height="100vh",
    )

# Crea la aplicación
app = rx.App()
app.add_page(index)
