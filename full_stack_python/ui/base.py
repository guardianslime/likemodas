# full_stack_python/ui/base.py (VERSIÓN MODIFICADA)

import reflex as rx
from ..auth.state import SessionState
from .dashboard import base_dashboard_page
from .. import navigation # Necesitamos navigation para los enlaces del menú

# --- ✨ NUEVO MENÚ FLOTANTE ✨ ---
# Este es el único menú para todas las páginas públicas.
def floating_hamburger_menu() -> rx.Component:
    """
    Un menú de hamburguesa flotante que se muestra en la esquina superior izquierda.
    Usa posicionamiento fijo para ser inmune a los conflictos de layout.
    """
    return rx.box(
        rx.menu.root(
            rx.menu.trigger(
                rx.button(rx.icon("menu", size=24), variant="soft", size="3")
            ),
            rx.menu.content(
                # Enlaces a todas las páginas públicas
                rx.menu.item("Home", on_click=navigation.NavState.to_home),
                rx.menu.item("Productos", on_click=navigation.NavState.to_pulic_galeri),
                rx.menu.item("Pricing", on_click=navigation.NavState.to_pricing),
                rx.menu.item("Contact", on_click=navigation.NavState.to_contact),
                rx.menu.separator(),
                rx.menu.item("Login", on_click=navigation.NavState.to_login),
                rx.menu.item("Register", on_click=navigation.NavState.to_register),
            ),
        ),
        # --- CSS que lo posiciona y lo mantiene fijo ---
        position="fixed", # Fijo en la pantalla, no se mueve con el scroll
        top="1.5rem",
        left="1.5rem",
        z_index="100", # Se asegura que esté por encima de todo
    )

# --- LAYOUT PÚBLICO MODIFICADO ---
# Este layout ahora solo muestra el menú flotante y el contenido.
def base_layout_component(child, *args, **kwargs) -> rx.Component:
    """El layout para usuarios NO autenticados."""
    return rx.fragment(
        floating_hamburger_menu(), # <--- Usa el nuevo menú
        rx.box(
            child,
            padding="1em",
            # Añadimos padding para que el contenido no se oculte debajo del menú
            padding_top="5rem", 
            width="100%",
            id="my-content-area-el"
        ),
        rx.color_mode.button(position="bottom-left"),
    )

# --- LAYOUT BASE PRINCIPAL (SIN CAMBIOS) ---
# Este sigue gestionando si el usuario está logueado o no.
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

# El navbar anterior (`public_navbar`) se ha eliminado por completo de este archivo.