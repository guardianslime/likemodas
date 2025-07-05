# full_stack_python/pages/dashboard.py

import reflex as rx
from ..articles.list import article_public_list_component
from ..articles.state import ArticlePublicState

def dashboard_component() -> rx.Component:
    return rx.box(
        rx.heading("Bienvenido de regreso", size='2'),
        rx.divider(margin_top='1em', margin_bottom='1em'),
        article_public_list_component(columns=3, limit=20),
        min_height="85vh",
        # La carga de datos se dispara cuando este componente se monta
        on_mount=ArticlePublicState.load_posts
    )