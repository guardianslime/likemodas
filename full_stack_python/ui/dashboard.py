import reflex as rx
from .sidebar import sidebar

def base_dashboard_page(child: rx.Component, *args, **kwargs) -> rx.Component:
    """
    Define la estructura base para todas las páginas autenticadas,
    colocando una barra lateral a la izquierda y el contenido principal a la derecha.
    """
    # Valida que el elemento hijo sea un componente válido de Reflex.
    if not isinstance(child, rx.Component):
        child = rx.heading("This is not a valid child element")
        
    # Devuelve un fragmento con la barra lateral y el contenido principal.
    return rx.fragment(
        rx.hstack(
            sidebar(),
            rx.box(
                child,
                padding="1em",
                width="100%",    
                id="my-content-area-el"
            ),
            # Asegura que la barra lateral y el contenido estén alineados en la parte superior.
            align="start" 
        ),
    )