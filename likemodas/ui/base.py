# likemodas/ui/base.py

import reflex as rx
from reflex.style import toggle_color_mode
from ..state import AppState
from .nav import public_navbar
from .skeletons import skeleton_navbar
# Importamos el nuevo componente principal del sidebar
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
    Estructura de página base simplificada que utiliza el nuevo sidebar deslizable
    para administradores, eliminando la duplicación de layouts.
    """
    return rx.cond(
        ~AppState.is_hydrated,
        # --- LAYOUT ESQUELETO ---
        rx.box(
            skeleton_navbar(),
            rx.box(
                child,
                padding_top="6rem", padding_x="1em", padding_bottom="1em", width="100%"
            ),
            width="100%",
        ),
        # --- LAYOUT HIDRATADO ---
        rx.cond(
            AppState.is_admin,
            # --- LAYOUT DE ADMIN (AHORA MUY SIMPLE) ---
            rx.box(
                # Simplemente llamamos al nuevo sidebar deslizable.
                # ¡No más encabezado ni lógica duplicada!
                sliding_admin_sidebar(),
                # El contenido principal de la página
                rx.box(
                    child,
                    padding="1em", # Un poco de padding para que no se pegue al borde
                    width="100%"
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