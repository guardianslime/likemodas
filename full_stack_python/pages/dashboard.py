import reflex as rx 

from ..articles.list import article_public_list_component

def dashboard_component() -> rx.Component:
    return rx.box(
        rx.heading("Welcome back", size='2'),
        rx.divider(),
        article_public_list_component(colums=3, limit=20),
        min_height="85vh",
    )