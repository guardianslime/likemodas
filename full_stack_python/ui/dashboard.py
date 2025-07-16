import reflex as rx
# Importa el nuevo componente de la galería
from ..articles.list import articles_gallery_page

def dashboard_component() -> rx.Component:
    """
    El componente del dashboard que se muestra al iniciar sesión.
    Ahora mostrará la nueva galería de artículos.
    """
    return rx.box(
        rx.heading("Bienvenido de regreso", size="5", margin_bottom="1em"),
        rx.divider(),
        # Usa el nuevo componente de galería
        articles_gallery_page(),
    )