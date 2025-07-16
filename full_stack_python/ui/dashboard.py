import reflex as rx

def dashboard_component() -> rx.Component:
    """
    Una versión simplificada del dashboard para solucionar el error de importación.
    """
    return rx.vstack(
        rx.heading("Bienvenido de regreso", size="7"),
        rx.text("Panel de control principal."),
        spacing="5",
        padding="2em",
        min_height="85vh",
    )