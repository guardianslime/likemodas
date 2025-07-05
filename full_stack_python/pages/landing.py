# full_stack_python/pages/landing.py

import reflex as rx
from .. import navigation
from ..articles.list import article_public_list_component
from ..articles.state import ArticlePublicState

def landing_component() -> rx.Component:
    return rx.vstack(
        rx.heading("Bienvenidos a Likemodas", size="9"),
        rx.link(
            rx.button("About us", color_scheme='gray'),
            href=navigation.routes.ABOUT_US_ROUTE
        ),
        rx.divider(),
        rx.heading("Recent Articles", size="5"),
        # --- CORRECCIÓN: Se elimina el argumento 'limit' ---
        article_public_list_component(columns=1),
        spacing="5",
        justify="center",
        align="center",
        min_height="85vh",
        id="my-child",
        on_mount=ArticlePublicState.load_posts
    )