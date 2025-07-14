# full_stack_python/ui/base.py (CORREGIDO)

import reflex as rx
from .sidebar import sidebar
from .search_state import SearchState
from ..auth.state import SessionState

def base_page(child: rx.Component, *args, **kwargs) -> rx.Component:
    """
    La plantilla base unificada y persistente para todas las páginas de la aplicación.
    """
    if not isinstance(child, rx.Component):
        child = rx.heading("This is not a valid child element")

    return rx.hstack(
        # La barra lateral siempre estará visible.
        sidebar(),
        
        # El contenido principal de la página.
        rx.vstack(
            # La barra de búsqueda, ahora integrada en la plantilla principal.
            rx.hstack(
                 rx.input(
                    placeholder="Buscar productos...",
                    value=SearchState.search_term,
                    on_change=SearchState.update_search,
                    on_blur=SearchState.search_action,
                    width="100%",
                    height="40px",
                    padding_x="4",
                    border_radius="full",
                    bg=rx.color("gray", 3),
                    border_width="0px",
                 ),
                 padding="1em",
                 width="100%",
                 border_bottom=f"1px solid {rx.color('gray', 6)}",
            ),
            
            # El contenido específico de cada página (el componente 'child').
            rx.box(
                child,
                padding="1em",
                width="100%",
                # Se ajusta la altura y se permite el scroll para el contenido
                height="calc(100vh - 73px)", 
                overflow_y="auto",
            ),
            
            # Botón para cambiar el modo de color.
            rx.color_mode.button(position="fixed", bottom="2em", right="2em", z_index="10"),
            
            width="100%",
            height="100vh",
            spacing="0",
            align_items="stretch",
        ),
        align_items="start",
        width="100%",
    )