# full_stack_python/ui/base.py (CÓDIGO COMPLETO)

import reflex as rx
from ..auth.state import SessionState
from .nav import public_navbar  # Se importa el nuevo navbar público
from .dashboard import base_dashboard_page

def base_layout_component(child, *args, **kwargs) -> rx.Component:
    """
    El layout para usuarios NO autenticados.
    Usa el nuevo navbar público y simple para evitar conflictos.
    """
    return rx.fragment(
        public_navbar(),
        rx.box(
            child,
            padding="1em",
            width="100%",
            id="my-content-area-el"
        ),
        rx.color_mode.button(position="bottom-left"),
    )

def base_page(child: rx.Component, *args, **kwargs) -> rx.Component:
    """
    Decide qué layout mostrar de forma segura, manejando el estado de hidratación.
    """
    if not isinstance(child, rx.Component):
        child = rx.heading("This is not a valid child element")
    
    # La estructura de `rx.cond` anidada es la solución.
    return rx.cond(
        SessionState.is_hydrated,  # 1. ¿Está el estado de sesión ya cargado?
        # SI: El estado es fiable. Ahora decidimos el layout.
        rx.cond(
            SessionState.is_authenticated,
            base_dashboard_page(child, *args, **kwargs),  # Hidratado y Autenticado
            base_layout_component(child, *args, **kwargs), # Hidratado y Público
        ),
        # NO: El estado aún no está cargado. Mostramos un spinner.
        rx.center(rx.spinner(), height="100vh") # Previene cualquier renderizado de layout.
    )