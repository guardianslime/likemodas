import reflex as rx
from ..articles.list import articles_gallery_page

def dashboard_component() -> rx.Component:
    return rx.box(
        rx.heading("Bienvenido de regreso", size="5", margin_bottom="1em"),
        rx.divider(),
        articles_gallery_page(),
    )