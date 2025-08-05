# likemodas/ui/base.py (VERSIÓN FINAL Y VERIFICADA)

import reflex as rx
from ..state import AppState
from .nav import public_navbar
# Asegúrate de tener skeleton_navbar en tus importaciones
from .skeletons import skeleton_navbar 
from .sidebar import sidebar, mobile_admin_menu, sidebar_dark_mode_toggle_item

def fixed_color_mode_button() -> rx.Component:
    return rx.box(
        rx.color_mode.button(),
        position="fixed", bottom="1.5rem", right="1.5rem", z_index="1000",
    )

def base_page(child: rx.Component, *args, **kwargs) -> rx.Component:
    """
    Esta es la estructura correcta que resuelve el problema.
    Renderiza un esqueleto estable en el servidor y el contenido real
    solo después de que el cliente esté completamente inicializado.
    """
    return rx.cond(
        ~AppState.is_hydrated,
        # --- LAYOUT ESQUELETO (Renderizado en Servidor) ---
        # Crea una estructura estable que no cambiará de tamaño.
        rx.box(
            skeleton_navbar(),
            rx.box(
                # La página hija (con su propio esqueleto) se renderiza aquí dentro.
                child,
                padding_top="6rem", padding_x="1em", padding_bottom="1em", width="100%"
            ),
            width="100%",
        ),
        # --- LAYOUT HIDRATADO (Renderizado en Cliente) ---
        # Se renderiza el layout real con estado, sin causar saltos.
        rx.cond(
            AppState.is_admin,
            # --- LAYOUT DE ADMIN ---
            rx.box(
                rx.vstack(
                    rx.hstack(
                        mobile_admin_menu(), rx.spacer(),
                        rx.image(src="/logo.png", width="6em", height="auto"),
                        rx.spacer(), sidebar_dark_mode_toggle_item(),
                        width="100%", padding="0.5em 1em", bg="#2C004B", align="center",
                    ),
                    rx.box(child, padding="1em", width="100%"),
                    display=["flex", "flex", "none", "none", "none"], spacing="0",
                ),
                rx.hstack(
                    sidebar(),
                    rx.box(child, padding="1em", width="100%"),
                    display=["none", "none", "flex", "flex", "flex"],
                    align="start", spacing="0", width="100%", min_height="100vh",
                ),
            ),
            # --- LAYOUT PÚBLICO ---
            rx.box(
                public_navbar(),
                rx.box(child, padding_top="6rem", padding_x="1em", padding_bottom="1em", width="100%"),
                fixed_color_mode_button(),
                width="100%",
            )
        )
    )