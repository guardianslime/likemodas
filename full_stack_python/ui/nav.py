# full_stack_python/ui/nav.py (CORREGIDO Y VERIFICADO)

import reflex as rx
from .. import navigation
from ..navigation.device import DeviceState
from .search_state import SearchState


def navbar() -> rx.Component:
    """
    Un navbar que muestra el logo, un menú de hamburguesa y una barra de búsqueda
    sin un color de fondo y usando Flexbox directamente para el layout.
    """
    return rx.box(
        # Contenedor principal usando Flexbox
        rx.box(
            # Grupo para el logo y el menú
            rx.box(
                # 🖼 LOGO
                rx.image(
                    src="/logo.jpg",
                    width=rx.breakpoints(sm="6em", md="8em", lg="10em"),
                    [cite_start]height="auto", [cite: 179]
                    border_radius="md",
                ),
                # ☰ Menú hamburguesa
                rx.menu.root(
                    rx.menu.trigger(
                        [cite_start]rx.icon("menu", box_size=rx.breakpoints(sm="2em", md="2.3em", lg="2.5em")) [cite: 180]
                    ),
                    rx.menu.content(
                        rx.menu.item("Home", on_click=navigation.NavState.to_home),
                        rx.menu.item("Articles", on_click=navigation.NavState.to_articles),
                        [cite_start]rx.menu.item("Blog", on_click=navigation.NavState.to_blog), [cite: 181]
                        rx.menu.item("Productos", on_click=navigation.NavState.to_pulic_galeri),
                        rx.menu.item("Pricing", on_click=navigation.NavState.to_pricing),
                        rx.menu.item("Contact", on_click=navigation.NavState.to_contact),
                        rx.menu.separator(),
                        [cite_start]rx.menu.item("Login", on_click=navigation.NavState.to_login), [cite: 182]
                        rx.menu.item("Register", on_click=navigation.NavState.to_register),
                    ),
                ),
                # Estilos para el grupo logo-menú
                style={
                    "display": "flex",
                    "align_items": "center",
                    "gap": "1rem",  # Espacio entre el logo y el menú
                }
            ),

            # 🔍 Barra de búsqueda estirada
            rx.input(
                [cite_start]placeholder="Buscar productos...", [cite: 183]
                value=SearchState.search_term,
                on_change=SearchState.update_search,
                on_blur=SearchState.search_action,
                width=rx.breakpoints(sm="55%", md="65%", lg="72%"),
                height=rx.breakpoints(sm="2.8em", md="3em", lg="3.3em"),
                [cite_start]padding_x="4", [cite: 184]
                border_radius="full",
                border_width="1px",
                border_color="#ccc",
                background_color="white",
                color="black",
                [cite_start]font_size=rx.breakpoints(sm="1", md="2", lg="3"), [cite: 185]
            ),

            # Estilos para el contenedor principal
            style={
                "display": "flex",
                "align_items": "center",
                "justify_content": "space-between",
                "width": "100%",
            }
        ),
        # Estilos y padding para el navbar completo
        padding_y="4",
        padding_x="6",
        width="100%",
        [cite_start]on_mount=DeviceState.on_mount, [cite: 186]
    )