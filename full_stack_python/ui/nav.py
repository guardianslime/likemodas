# full_stack_python/ui/nav.py (CÓDIGO CORREGIDO Y UNIFICADO)

import reflex as rx
from .. import navigation
from ..navigation.device import DeviceState
from .search_state import SearchState

def public_navbar() -> rx.Component:
    """
    Una barra de navegación superior fija para todas las páginas públicas.
    Integra el menú, el logo y la barra de búsqueda para una experiencia de usuario consistente.
    """
    return rx.box(
        rx.hstack(
            # Lado Izquierdo: Menú y Logo
            rx.hstack(
                # Menú de Hamburguesa (lógica del menú flotante anterior)
                rx.menu.root(
                    rx.menu.trigger(
                        rx.button(rx.icon("menu", size=24), variant="soft", size="3")
                    ),
                    rx.menu.content(
                        rx.menu.item("Home", on_click=navigation.NavState.to_home),
                        rx.menu.item("Productos", on_click=navigation.NavState.to_pulic_galeri),
                        rx.menu.item("Pricing", on_click=navigation.NavState.to_pricing),
                        rx.menu.item("Contact", on_click=navigation.NavState.to_contact),
                        rx.menu.separator(),
                        rx.menu.item("Login", on_click=navigation.NavState.to_login),
                        rx.menu.item("Register", on_click=navigation.NavState.to_register),
                    ),
                ),
                # Logo
                rx.image(
                    src="/logo.jpg",
                    width="8em", # Ancho similar a "Likemodas"
                    height="auto",
                    border_radius="md",
                ),
                align="center",
                spacing="4",
            ),
            
            # Lado Derecho: Barra de Búsqueda
            rx.input(
                placeholder="Buscar productos...",
                value=SearchState.search_term,
                on_change=SearchState.update_search,
                on_blur=SearchState.search_action,
                width=["60%", "65%", "70%", "72%"], # Responsivo
                height=["2.5em", "2.8em", "3em", "3.3em"],
                padding_x="4",
                border_radius="full",
                border_width="1px",
                font_size=rx.breakpoints(sm="2", md="3", lg="3"),
            ),
            justify="between",
            align="center",
            width="100%",
        ),
        # Estilos para la barra de navegación fija
        position="fixed",
        top="0",
        left="0",
        right="0",
        width="100%",
        padding="0.75rem 1rem",
        z_index="99",
        bg=rx.color_mode_cond("#ffffffF0", "#1D2330F0"), # Fondo con transparencia
        style={"backdrop_filter": "blur(10px)"},
        on_mount=DeviceState.on_mount,
    )


# El resto del código del archivo (navbar original y SearchState) permanece igual.
# ... (código existente no modificado) ...
# full_stack_python/ui/nav.py (CÓDIGO COMPLETO)

import reflex as rx
from .. import navigation
from ..navigation.device import DeviceState
from .search_state import SearchState

def public_navbar() -> rx.Component:
    """
    Una barra de navegación superior fija para todas las páginas públicas.
    Integra el menú, el logo y la barra de búsqueda para una experiencia de usuario consistente.
    """
    return rx.box(
        rx.hstack(
            # Lado Izquierdo: Menú y Logo
            rx.hstack(
                # Menú de Hamburguesa (lógica del menú flotante anterior)
                rx.menu.root(
                    rx.menu.trigger(
                        rx.button(rx.icon("menu", size=24), variant="soft", size="3")
                    ),
                    rx.menu.content(
                        rx.menu.item("Home", on_click=navigation.NavState.to_home),
                        rx.menu.item("Productos", on_click=navigation.NavState.to_pulic_galeri),
                        rx.menu.item("Pricing", on_click=navigation.NavState.to_pricing),
                        rx.menu.item("Contact", on_click=navigation.NavState.to_contact),
                        rx.menu.separator(),
                        rx.menu.item("Login", on_click=navigation.NavState.to_login),
                        rx.menu.item("Register", on_click=navigation.NavState.to_register),
                    ),
                ),
                # Logo
                rx.image(
                    src="/logo.jpg",
                    width="8em", # Ancho similar a "Likemodas"
                    height="auto",
                    border_radius="md",
                ),
                align="center",
                spacing="4",
            ),
            
            # Lado Derecho: Barra de Búsqueda
            rx.input(
                placeholder="Buscar productos...",
                value=SearchState.search_term,
                on_change=SearchState.update_search,
                on_blur=SearchState.search_action,
                width=["60%", "65%", "70%", "72%"], # Responsivo
                height=["2.5em", "2.8em", "3em", "3.3em"],
                padding_x="4",
                border_radius="full",
                border_width="1px",
                font_size=rx.breakpoints(sm="2", md="3", lg="3"),
            ),
            justify="between",
            align="center",
            width="100%",
        ),
        # Estilos para la barra de navegación fija
        position="fixed",
        top="0",
        left="0",
        right="0",
        width="100%",
        padding="0.75rem 1rem",
        z_index="99",
        bg=rx.color_mode_cond("#ffffffF0", "#1D2330F0"), # Fondo con transparencia
        style={"backdrop_filter": "blur(10px)"},
        on_mount=DeviceState.on_mount,
    )


def navbar() -> rx.Component:
    """
    Navbar original y completo. Ya no se usa en el layout público,
    pero se mantiene aquí por si se necesita en otras partes.
    """
    return rx.box(
        # Grupo Izquierdo: Logo y Menú
        rx.box(
            rx.image(
                src="/logo.jpg",
                width=rx.breakpoints(sm="6em", md="8em", lg="10em"),
                height="auto",
                border_radius="md",
            ),
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
            style={
                "display": "flex",
                "align_items": "center",
                "gap": "1rem",
            }
        ),
        # Barra de Búsqueda
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
        # Estilos del contenedor principal
        style={
            "display": "flex",
            "align_items": "center",
            "justify_content": "space-between",
            "width": "100%",
            "padding_y": "0.75rem",
            "padding_x": "1rem",
        },
        on_mount=DeviceState.on_mount,
    )


import reflex as rx

class SearchState(rx.State):
    search_term: str = ""

    def update_search(self, value: str):
        self.search_term = value
        print(f"🔍 Buscando: {self.search_term}")

    def search_action(self):
        # Aquí puedes navegar a otra página o hacer un filtro
        print(f"🔎 Acción de búsqueda: {self.search_term}")