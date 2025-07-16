import reflex as rx
# Importa el componente con el nombre nuevo y correcto
from ..articles.list import articles_gallery_page

def dashboard_component() -> rx.Component:
    """
    El componente del dashboard que se muestra al iniciar sesión.
    """
    return rx.box(
        rx.heading("Bienvenido de regreso", size="5", margin_bottom="1em"),
        rx.divider(),
        # Usa el componente con el nombre nuevo
        articles_gallery_page(),
    )