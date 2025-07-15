# full_stack_python/ui/base.py (CÓDIGO CORREGIDO Y UNIFICADO)

import reflex as rx
from ..auth.state import SessionState
from .dashboard import base_dashboard_page
from .nav import public_navbar # ✨ CAMBIO: Importamos la nueva navbar unificada

# --- ✨ NUEVO BOTÓN DE MODO OSCURO FIJO ✨ ---
def fixed_color_mode_button() -> rx.Component:
    """
    Un botón de cambio de tema que se mantiene fijo en la esquina inferior derecha.
    Su posición es inmune al scroll o al layout de la página.
    """
    return rx.box(
        rx.color_mode.button(),
        position="fixed",
        bottom="1.5rem",
        right="1.5rem",
        z_index="100", # Se asegura que esté por encima de otros elementos
    )

# --- LAYOUT PÚBLICO MODIFICADO ---
def base_layout_component(child, *args, **kwargs) -> rx.Component:
    """El layout para usuarios NO autenticados."""
    return rx.fragment(
        public_navbar(), # <--- ✨ CAMBIO: Usa la nueva navbar superior
        rx.box(
            child,
            padding="1em",
            # Añadimos padding superior para que el contenido no se oculte debajo de la navbar fija
            padding_top="6rem", 
            width="100%",
            id="my-content-area-el"
        ),
        fixed_color_mode_button(), # <--- ✨ CAMBIO: Usa el nuevo botón de tema fijo
    )

# --- LAYOUT BASE PRINCIPAL (SIN CAMBIOS) ---
def base_page(child: rx.Component, *args, **kwargs) -> rx.Component:
    if not isinstance(child, rx.Component):
        child = rx.heading("This is not a valid child element")
    return rx.cond(
        SessionState.is_hydrated,
        rx.cond(
            SessionState.is_authenticated,
            base_dashboard_page(child, *args, **kwargs),
            base_layout_component(child, *args, **kwargs),
        ),
        rx.center(rx.spinner(), height="100vh")
    )

# ... (código existente no modificado como base_dashboard_page, etc.) ...
import reflex as rx

from .sidebar import sidebar

def base_dashboard_page(child: rx.Component, *args, **kwargs) -> rx.Component:
    # print(type(x) for x in args)
    if not isinstance(child, rx.Component):
        child = rx.heading("This is not valid child element")
    return rx.fragment(
        rx.hstack(
            sidebar(),
            rx.box(
                child,
                #bg=rx.color("accent", 3),
                padding="1em",
                width="100%",    
                id="my-content-area-el"
            ),
        ),
        # rx.color_mode.button(position= "bottom-left"),
        # padding="10em",
        # id="my-base-container",
    )