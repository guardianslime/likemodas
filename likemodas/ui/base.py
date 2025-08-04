# likemodas/ui/base.py

import reflex as rx
from..auth.state import SessionState
from.nav import public_navbar
from.sidebar import sidebar

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
    Layout base que implementa un patrón de carga seguro para prevenir
    el "salto" de la interfaz al esperar la hidratación del estado.
    """
    # 🛡️ Patrón de renderizado condicional recomendado
    return rx.cond(
        ~SessionState.is_hydrated,
        
        # 1. MIENTRAS EL ESTADO NO ESTÉ HIDRATADO: Muestra un loader.
        rx.center(rx.spinner(size="3"), height="100vh"),
        
        # 2. CUANDO EL ESTADO ESTÁ HIDRATADO: Decide qué layout mostrar.
        rx.cond(
            SessionState.is_admin,
            
            # 2a. Si es ADMIN, muestra el layout con sidebar.
            rx.hstack(
                sidebar(),
                rx.box(
                    child,
                    padding="1em",
                    width="100%",
                ),
                align="start",
                spacing="0",
                width="100%",
                min_height="100vh",
            ),
            
            # 2b. Si es PÚBLICO, muestra el layout con navbar.
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