# full_stack_python/ui/nav.py (SOLUCIÓN GLOBAL)

import reflex as rx
from .. import navigation
from ..navigation.device import DeviceState
from .search_state import SearchState

def navbar() -> rx.Component:
    """
    Navbar global y estable para toda la aplicación.
    Usa un layout de Flexbox directo para máxima compatibilidad y consistencia.
    """
    return rx.box(
        # Grupo Izquierdo: Logo y Menú
        rx.box(
            # Logo
            rx.image(
                src="/logo.jpg",
                width=rx.breakpoints(sm="6em", md="8em", lg="10em"),
                height="auto",
                border_radius="md",
            ),
            # Menú de hamburguesa
            rx.menu.root(
                rx.menu.trigger(
                    rx.icon("menu", box_size=rx.breakpoints(sm="2em", md="2.3em", lg="2.5em"))
                ),
                rx.menu.content(
                    rx.menu.item("Home", on_click=navigation.NavState.to_home),
                    rx.menu.item("Articles", on_click=navigation.NavState.to_articles),
                    rx.menu.item("Blog", on_click=navigation.NavState.to_blog),
                    rx.menu.item("Productos", on_click=navigation.NavState.to_pulic_galeri),
                    rx.menu.item("Pricing", on_click=navigation.NavState.to_pricing),
                    rx.menu.item("Contact", on_click=navigation.NavState.to_contact),
                    rx.menu.separator(),
                    rx.menu.item("Login", on_click=navigation.NavState.to_login),
                    rx.menu.item("Register", on_click=navigation.NavState.to_register),
                ),
            ),
            # Estilos para el grupo izquierdo
            style={
                "display": "flex",
                "align_items": "center",
                "gap": "1rem",  # Espacio entre logo y menú
            }
        ),

        # Barra de Búsqueda (ocupará el espacio restante)
        rx.input(
            placeholder="Buscar productos...",
            value=SearchState.search_term,
            on_change=SearchState.update_search,
            on_blur=SearchState.search_action,
            width=rx.breakpoints(sm="55%", md="65%", lg="72%"),
            height=rx.breakpoints(sm="2.8em", md="3em", lg="3.3em"),
            padding_x="4",
            border_radius="full",
            border_width="1px",
            border_color="#ccc",
            background_color="white",
            color="black",
            font_size=rx.breakpoints(sm="1", md="2", lg="3"),
        ),
        
        # Estilos del contenedor principal del navbar
        style={
            "display": "flex",
            "align_items": "center",
            "justify_content": "space-between", # Empuja los grupos a los extremos
            "width": "100%",
            "padding_y": "0.75rem",
            "padding_x": "1rem",
        },
        on_mount=DeviceState.on_mount,
    )