# full_stack_python/ui/base.py (REESTRUCTURADO)

import reflex as rx
from .sidebar import sidebar
from .search_state import SearchState
from ..auth.state import SessionState

def search_bar_component() -> rx.Component:
    """La barra de búsqueda que aparecerá en la parte superior del contenido."""
    return rx.hstack(
        # El trigger del menú en móvil ahora está en el componente sidebar
        rx.box(display=["flex", "flex", "none", "none"]), # Espacio para el trigger
        rx.input(
            placeholder="Buscar productos...",
            value=SearchState.search_term,
            on_change=SearchState.update_search,
            on_blur=SearchState.search_action,
            width="100%",
            height=rx.breakpoints(sm="2.8em", md="3em", lg="3.3em"),
            padding_x="4",
            border_radius="full",
            border_width="1px",
            border_color="#ccc",
            background_color="white",
            color="black",
            font_size=rx.breakpoints(sm="1", md="2", lg="3"),
        ),
        padding_y="2",
        padding_x="4",
        width="100%",
        align_items="center",
    )

def base_page(child: rx.Component, *args, **kwargs) -> rx.Component:
    """La plantilla base unificada para todas las páginas."""
    if not isinstance(child, rx.Component):
        child = rx.heading("This is not a valid child element")

    return rx.hstack(
        sidebar(),  # La barra lateral siempre está presente
        rx.vstack(
            search_bar_component(), # La barra de búsqueda siempre está presente
            rx.box(
                child,
                padding="1em",
                width="100%",
                height="calc(100vh - 80px)", # Ajusta la altura para el scroll
                overflow_y="auto", # Habilita el scroll vertical para el contenido
            ),
            rx.color_mode.button(position="fixed", bottom="2em", right="2em", z_index="10"),
            spacing="0",
            width="100%",
            align_items="stretch", # Estira los hijos para ocupar el ancho
        ),
        width="100%",
        align_items="start",
    )