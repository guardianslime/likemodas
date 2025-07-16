# full_stack_python/ui/base.py

import reflex as rx
from ..auth.state import SessionState
from .nav import public_navbar 
from .sidebar import sidebar

# --- ✨ LAYOUT PARA USUARIOS AUTENTICADOS (CON SIDEBAR) ✨ ---
def protected_layout(child: rx.Component) -> rx.Component:
    """El layout para usuarios autenticados, con la barra lateral."""
    return rx.hstack(
        sidebar(),
        rx.box(
            child,
            padding="1em",
            width="100%",    
            id="my-content-area-el"
        ),
        align="start"
    )

# --- ✨ LAYOUT PARA PÁGINAS PÚBLICAS (CON NAVBAR SUPERIOR) ✨ ---
def public_layout(child: rx.Component) -> rx.Component:
    """El layout para usuarios no autenticados, con la barra de navegación superior."""
    return rx.fragment(
        public_navbar(),
        rx.box(
            child,
            padding="1em",
            padding_top="6rem", # Espacio para la navbar fija
            width="100%",
            id="my-content-area-el"
        ),
        # Puedes añadir aquí el botón de modo oscuro si lo deseas para páginas públicas
        # rx.color_mode.button(position="fixed", bottom="1.5rem", right="1.5rem")
    )

# --- ✨ FUNCIÓN PRINCIPAL `base_page` ✨ ---
# Esta función decide qué layout usar basado en el estado de autenticación.
# Ya no necesita importar `base_dashboard_page` porque esa lógica ahora está aquí.
def base_page(child: rx.Component, *args, **kwargs) -> rx.Component:
    """
    Función principal que envuelve todo el contenido y elige el layout
    adecuado (público o protegido) según si el usuario está logueado.
    """
    if not isinstance(child, rx.Component):
        child = rx.heading("This is not a valid child element")
        
    return rx.cond(
        SessionState.is_hydrated,
        rx.cond(
            SessionState.is_authenticated,
            protected_layout(child), # Si está autenticado, usa el layout con sidebar
            public_layout(child),      # Si no, usa el layout público
        ),
        # Muestra un spinner mientras se verifica el estado de autenticación
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