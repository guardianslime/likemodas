# likemodas/ui/base.py

import reflex as rx
# Se importa el estado base (SessionState) en lugar del estado completo (AppState)
from ..auth.state import SessionState
from .nav import public_navbar
from .sidebar import sidebar, mobile_admin_menu, sidebar_dark_mode_toggle_item

def fixed_color_mode_button() -> rx.Component:
    """Un botón de cambio de tema que se renderiza solo en el cliente."""
    return rx.box(
        rx.color_mode.button(),
        position="fixed",
        bottom="1.5rem",
        right="1.5rem",
        z_index="1000",
    )

def base_page(child: rx.Component, *args, **kwargs) -> rx.Component:
    """
    Layout base que implementa un patrón de carga seguro y ahora es
    completamente responsivo para todos los tipos de usuario.
    """
    # Se usa SessionState para las comprobaciones, rompiendo el ciclo de importación.
    return rx.cond(
        ~SessionState.is_hydrated,
        
        # 1. Muestra un spinner mientras el estado no esté listo.
        rx.center(rx.spinner(size="3"), height="100vh"),
        
        # 2. Cuando el estado está hidratado, decide qué layout mostrar.
        rx.cond(
            SessionState.is_admin,
            
            # --- 2a. LAYOUT DE ADMIN RESPONSIVO ---
            rx.box(
                # --- Layout para Móvil (sm y menor) ---
                rx.vstack(
                    rx.hstack(
                        mobile_admin_menu(), # Menú de hamburguesa
                        rx.spacer(),
                        rx.image(src="/logo.png", width="6em", height="auto"),
                        rx.spacer(),
                        sidebar_dark_mode_toggle_item(), # Botón de tema
                        width="100%",
                        padding="0.5em 1em",
                        bg="#2C004B",
                        align="center",
                    ),
                    rx.box(
                        child,
                        padding="1em",
                        width="100%",
                    ),
                    display=["flex", "flex", "none", "none", "none"], # Visible en móvil
                    spacing="0",
                ),

                # --- Layout para Escritorio (md y mayor) ---
                rx.hstack(
                    sidebar(), # Barra lateral completa
                    rx.box(
                        child,
                        padding="1em",
                        width="100%",
                    ),
                    display=["none", "none", "flex", "flex", "flex"], # Visible en escritorio
                    align="start",
                    spacing="0",
                    width="100%",
                    min_height="100vh",
                ),
            ),
            
            # --- 2b. LAYOUT PÚBLICO (sin cambios) ---
            rx.box(
                public_navbar(),
                rx.box(
                    child,
                    padding_top="6rem",
                    padding_x="1em",
                    padding_bottom="1em",
                    width="100%",
                ),
                fixed_color_mode_button(),
                width="100%",
            )
        )
    )