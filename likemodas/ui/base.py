# likemodas/ui/base.py

import reflex as rx
from reflex.style import toggle_color_mode
from ..state import AppState
from .nav import public_navbar
# Se quita la importación de skeleton_navbar porque usaremos un spinner
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
            radius="full"
        ),
        position="fixed", bottom="1.5rem", right="1.5rem", z_index="1000",
    )

def base_page(child: rx.Component, *args, **kwargs) -> rx.Component:
    """
    Estructura de página base con centrado forzado para el contenido de admin.
    """
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
            # --- LAYOUT DE ADMIN CORREGIDO ---
            rx.box(
                sliding_admin_sidebar(),
                # --- CAMBIO CLAVE: Centramos el contenedor del child ---
                rx.center(
                    # El child (tu página) ahora está dentro de un rx.center
                    rx.box(
                        child,
                        padding="1em",
                        width="100%",
                    ),
                    width="100%", # El center ocupa todo el ancho disponible
                ),
                width="100%",
                min_height="100vh",
            ),
            # --- LAYOUT PÚBLICO (Sin cambios) ---
            rx.box(
                public_navbar(),
                rx.box(child, padding_top="6rem", padding_x="1em", padding_bottom="1em", width="100%"),
                fixed_color_mode_button(),
                width="100%",
            )
        )
    )