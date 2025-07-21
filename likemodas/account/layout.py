# likemodas/account/layout.py

import reflex as rx
from .sidebar import account_sidebar

def account_layout(child: rx.Component) -> rx.Component:
    """Layout que envuelve las páginas de la sección Mi Cuenta."""
    return rx.hstack(
        account_sidebar(),
        rx.box(
            child,
            padding="2em",
            width="100%",
        ),
        align_items="start",
        min_height="85vh",
        width="100%"
    )