# likemodas/ui/base.py (Código completo y corregido)

import reflex as rx
from reflex.style import toggle_color_mode
from ..state import AppState
from .nav import public_navbar
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
            # --- LAYOUT DE ADMIN RESPONSIVO ---
            rx.box(
                admin_sidebar(),          # Sidebar para escritorio (se oculta solo en móvil)
                admin_mobile_sidebar(),   # Botón y drawer para móvil (se oculta solo en escritorio)
                rx.box(
                    child,
                    # Margen izquierdo responsivo: 0 en móvil, ancho del sidebar en escritorio
                    margin_left=["0", "0", "16em"],
                    padding_y="2em",
                    padding_x=["1em", "1em", "4em"], # Menos padding en móvil
                    width="100%",
                ),
                fixed_color_mode_button(),
            ),
            # --- LAYOUT PÚBLICO (sin cambios) ---
            rx.box(
                public_navbar(),
                rx.box(child, padding_top="6rem", padding_x="1em", padding_bottom="1em", width="100%"),
                fixed_color_mode_button(),
                width="100%",
            )
        )
    )