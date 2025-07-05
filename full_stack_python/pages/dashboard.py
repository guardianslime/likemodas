# full_stack_python/pages/dashboard.py

import reflex as rx
from ..articles.list import article_public_list_component
from ..articles.state import ArticlePublicState

def dashboard_component() -> rx.Component:
    return rx.box(
        rx.heading("Bienvenido de regreso", size='2'),
        rx.divider(margin_top='1em', margin_bottom='1em'),
        # --- CORRECCIÓN: Se elimina el argumento 'limit' ---
        article_public_list_component(columns=3),
        min_height="85vh",
        on_mount=ArticlePublicState.load_posts
    )