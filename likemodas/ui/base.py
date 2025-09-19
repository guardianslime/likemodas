# likemodas/ui/base.py (Código completo y corregido)

import reflex as rx
from reflex.style import toggle_color_mode
from ..state import AppState
from .nav import public_navbar
# --- MODIFICACIÓN: Importamos los nuevos componentes del sidebar ---
from .sidebar import admin_sidebar, admin_mobile_sidebar

def fixed_color_mode_button() -> rx.Component:
    """Botón flotante para cambiar el modo de color."""
    return rx.box(
        rx.button(
            rx.color_mode_cond(
                light=rx.icon(tag="sun"),
                dark=rx.icon(tag="moon")
            ),
            on_click=toggle_color_mode,
            variant="soft",
            radius="full",
            color_scheme="violet"
        ),
        position="fixed", bottom="1.5rem", right="1.5rem", z_index="1000",
    )

def admin_header() -> rx.Component:
    """
    Un nuevo header para la vista de admin que contiene el botón de hamburguesa
    y solo es visible en pantallas pequeñas.
    """
    return rx.hstack(
        rx.drawer.trigger(
            rx.icon_button(
                rx.icon("menu", size=24),
                variant="ghost",
                color_scheme="gray",
            )
        ),
        # --- LÓGICA RESPONSIVA: Oculto en pantallas grandes (md y superiores) ---
        display=["flex", "flex", "none"],
        position="sticky",
        top="0",
        left="0",
        width="100%",
        padding="0.5em 1em",
        z_index="999",
        bg=rx.color("gray", 2),
        style={"backdrop_filter": "blur(10px)"},
    )

def base_page(child: rx.Component, *args, **kwargs) -> rx.Component:
    """Estructura de página base que ahora incluye el layout de admin responsivo."""
    loading_screen = rx.center(
        rx.spinner(size="3"),
        height="100vh",
        width="100%",
        background=rx.color("gray", 2)
    )

    return rx.cond(
        ~AppState.is_hydrated,
        loading_screen,
        rx.cond(
            AppState.is_admin,
            # --- INICIO: NUEVO LAYOUT DE ADMIN RESPONSIVO ---
            rx.box(
                admin_sidebar(),          # El sidebar fijo para escritorio
                admin_mobile_sidebar(),   # El cajón deslizable para móvil
                rx.box(
                    admin_header(),       # El header con el botón de hamburguesa para móvil
                    child,
                    # --- LÓGICA RESPONSIVA ---
                    # Sin margen en móvil, con margen en escritorio para hacer espacio al sidebar
                    margin_left=["0", "0", "16em"],
                    padding="2em",
                    width="100%",
                ),
                fixed_color_mode_button(),
            ),
            # --- FIN: NUEVO LAYOUT DE ADMIN RESPONSIVO ---
            rx.box(
                public_navbar(),
                rx.box(child, padding_top="6rem", padding_x="1em", padding_bottom="1em", width="100%"),
                fixed_color_mode_button(),
                width="100%",
            )
        )
    )