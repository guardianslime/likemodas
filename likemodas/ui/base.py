# likemodas/ui/base.py

import reflex as rx
from reflex.style import toggle_color_mode
from ..state import AppState
from .nav import public_navbar
from .skeletons import skeleton_navbar
from .sidebar import sidebar, sidebar_dark_mode_toggle_item

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

def admin_header() -> rx.Component:
    """El nuevo encabezado para la vista de administrador."""
    return rx.hstack(
        # Botón para mostrar/ocultar el nuevo sidebar deslizable
        rx.icon_button(
            rx.icon("menu", size=24),
            on_click=AppState.toggle_admin_sidebar,
            variant="ghost",
            color_scheme="gray"
        ),
        rx.spacer(),
        rx.image(src="/logo.png", width="6em", height="auto"),
        rx.spacer(),
        sidebar_dark_mode_toggle_item(),
        position="fixed",
        top="0",
        left="0",
        right="0",
        width="100%",
        padding="0.5em 1em",
        bg="#2C004B",
        align="center",
        z_index=999, # Debe estar por debajo del sidebar
    )

def base_page(child: rx.Component, *args, **kwargs) -> rx.Component:
    """
    Estructura de página base simplificada que resuelve el problema de duplicación
    y utiliza el nuevo sidebar deslizable para administradores.
    """
    return rx.cond(
        ~AppState.is_hydrated,
        # --- LAYOUT ESQUELETO (Sin cambios) ---
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
            # --- NUEVO Y SIMPLIFICADO LAYOUT DE ADMIN ---
            rx.box(
                admin_header(), # El nuevo encabezado fijo
                sidebar(),      # El nuevo sidebar deslizable
                rx.box(
                    child, 
                    padding_top="4rem",  # Espacio para el encabezado
                    padding_x="1em", 
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