# likemodas/ui/base.py (Código completo y corregido)

import reflex as rx
from reflex.style import toggle_color_mode
from ..state import AppState
from .nav import public_navbar
from .sidebar import sliding_admin_sidebar

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
    """Estructura de página base que ahora incluye el botón flotante en ambas vistas."""
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
            # --- LAYOUT DE ADMIN ---
            rx.box(
                sliding_admin_sidebar(),
                rx.box(
                    child,
                    padding_x="4em",
                    padding_y="2em",
                    width="100%"
                ),
                
                # --- CORRECCIÓN: AÑADIMOS EL BOTÓN FLOTANTE AQUÍ ---
                fixed_color_mode_button(),

                width="100%",
                min_height="100vh",
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