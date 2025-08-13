# likemodas/account/sidebar.py

import reflex as rx
from .. import navigation

def account_sidebar() -> rx.Component:
    """El menú lateral para la página Mi Cuenta del usuario."""
    return rx.vstack(
        rx.heading("Mi Cuenta", size="6", margin_bottom="1em"),
        rx.link(
            rx.text("Mis Compras"),
            href=navigation.routes.PURCHASE_HISTORY_ROUTE,
            width="100%",
            padding="0.5em",
        ),
        rx.link(
            rx.text("Información para envíos"),
            href=navigation.routes.SHIPPING_INFO_ROUTE,
            width="100%",
            padding="0.5em",
        ),
        align_items="start",
        padding="1em",
        border_right="1px solid #ededed",
        height="100%",
        min_width="250px"
    )
