# En likemodas/account/sidebar.py

import reflex as rx
from .. import navigation
from ..state import AppState

def sidebar_link(text: str, href: str) -> rx.Component:
    """Un componente reutilizable para cada enlace del menú."""
    is_active = AppState.current_path == href
    
    return rx.link(
        rx.text(text),
        href=href,
        width="100%",
        padding="0.75em",
        bg=rx.cond(is_active, rx.color("violet", 4), "transparent"),
        color=rx.cond(is_active, rx.color("violet", 11), rx.color_mode_cond("black", "white")),
        font_weight=rx.cond(is_active, "bold", "normal"),
        border_radius="var(--radius-3)",
        _hover={
            "background_color": rx.color("violet", 5),
            "color": rx.color("violet", 11),
        },
    )

def account_sidebar() -> rx.Component:
    """Sidebar con diseño mejorado para la sección Mi Cuenta."""
    return rx.vstack(
        rx.heading("Mi Cuenta", size="7", margin_bottom="0.5em", padding_x="0.75em"),
        sidebar_link("Mi Perfil", "/my-account/profile"),
        sidebar_link("Mis Compras", navigation.routes.PURCHASE_HISTORY_ROUTE),
        sidebar_link("Información para envíos", navigation.routes.SHIPPING_INFO_ROUTE),
        sidebar_link("Publicaciones Guardadas", "/my-account/saved-posts"),
        align_items="start",
        padding="1em",
        border_right=f"1px solid {rx.color('gray', 6)}",
        height="100%",
        min_width="250px",
        spacing="2",
    )