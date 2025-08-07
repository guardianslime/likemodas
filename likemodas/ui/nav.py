import reflex as rx
from ..state import AppState

def public_navbar() -> rx.Component:
    """
    Una barra de navegación de prueba, ultra simple, para aislar el error.
    Si esta barra aparece, el problema está en la navbar original.
    """
    return rx.box(
        rx.hstack(
            rx.heading("Likemodas (Modo de Prueba)", color="white"),
            rx.spacer(),
            rx.text("Navbar Cargada Correctamente", color="white"),
            align="center",
            width="100%",
        ),
        bg="blue",  # Un color llamativo para que sea obvio
        position="fixed",
        top="0",
        left="0",
        right="0",
        width="100%",
        padding="1rem 1.5rem",
        z_index="999",
        height="6rem", # Altura fija consistente con tu padding
    )