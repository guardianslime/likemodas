#full_stack_python/pages/dashboard.py

import reflex as rx 

from ..articles.list import article_public_list_component

def dashboard_component() -> rx.Component:
    return rx.box(
        rx.heading("Bienvenido de regreso", size='2'),
        rx.divider(margin_top='1em', mangin_bottom='1em'),
        article_public_list_component(columns=3, limit=20),
        min_height="85vh",
    )
