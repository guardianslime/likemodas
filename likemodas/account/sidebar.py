# En likemodas/account/sidebar.py

import reflex as rx
from .. import navigation
from ..state import AppState # ✨ Asegúrate de que AppState esté importado

def sidebar_link(text: str, href: str) -> rx.Component:
    """Un componente reutilizable para cada enlace del menú."""
    is_active = AppState.current_path == href
    
    return rx.link(
        rx.text(text),
        href=href,
        width="100%",
        padding="0.75em",
        # Estilo condicional: resalta el enlace si la página está activa
        bg=rx.cond(is_active, rx.color("violet", 4), "transparent"),
        color=rx.cond(is_active, rx.color("violet", 11), rx.color_mode_cond("black", "white")),
        font_weight=rx.cond(is_active, "bold", "normal"),
        border_radius="var(--radius-3)",
        # Efecto al pasar el mouse por encima
        _hover={
            "background_color": rx.color("violet", 4),
            "color": rx.color("violet", 11),
        },
    )

def account_sidebar() -> rx.Component:
    return rx.vstack(
        rx.heading("Mi Cuenta", size="6", margin_bottom="1em"),
        
        # Usamos el nuevo componente para cada enlace
        sidebar_link("Mi Perfil", "/my-account/profile"),
        sidebar_link("Mis Compras", navigation.routes.PURCHASE_HISTORY_ROUTE),
        sidebar_link("Información para envíos", navigation.routes.SHIPPING_INFO_ROUTE),
        sidebar_link("Publicaciones Guardadas", "/my-account/saved-posts"),
        
        align_items="start",
        padding="1em",
        border_right="1px solid #ededed",
        height="100%",
        min_width="250px",
        spacing="2", # Un poco de espacio entre los elementos
    )