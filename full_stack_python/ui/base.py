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

def public_navbar() -> rx.Component:
    return rx.box(
        rx.menu.root(...),
        style={
            "display": "flex",
            "justify_content": "flex-end", # Aligns menu to the right
            "width": "100%",
            "padding": "1rem",
        },
        #...
    )