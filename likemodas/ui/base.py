# likemodas/ui/base.py

import reflex as rx
from ..auth.state import SessionState
from .nav import public_navbar 
from .sidebar import sidebar
from .filter_panel import floating_filter_panel 

# --- ✨ FUNCIÓN RESTAURADA ✨ ---
def fixed_color_mode_button() -> rx.Component:
    """Un botón de cambio de tema que se mantiene fijo en la esquina inferior derecha."""
    return rx.box(
        rx.color_mode.button(),
        position="fixed",
        bottom="1.5rem",
        right="1.5rem",
        z_index="100",
    )

def protected_layout(child: rx.Component) -> rx.Component:
    """El layout para usuarios autenticados, ahora comprueba la verificación."""
    return rx.hstack(
        sidebar(),
        rx.box(
            # Comprueba si el usuario está verificado
            rx.cond(
                SessionState.authenticated_user_info.is_verified,
                child,  # Si está verificado, muestra el contenido
                # Si no, muestra un mensaje de advertencia
                rx.center(
                    rx.vstack(
                        rx.heading("Verificación Requerida"),
                        rx.text("Por favor, revisa tu correo electrónico para verificar tu cuenta antes de continuar."),
                        # Podrías añadir un botón para reenviar el correo aquí
                        spacing="4"
                    ),
                    height="80vh"
                )
            ),
            padding="1em",
            width="100%",
            id="my-content-area-el"
        ),
        align="start"
    )

def public_layout(child: rx.Component) -> rx.Component:
    """El layout para usuarios no autenticados y clientes, con la barra de navegación superior."""
    return rx.fragment(
        public_navbar(),
        rx.box(
            child,
            padding="1em",
            padding_top="6rem", 
            width="100%",
            id="my-content-area-el"
        ),
        fixed_color_mode_button()
    )

def base_page(child: rx.Component, *args, **kwargs) -> rx.Component:
    """
    Función principal que envuelve todo el contenido y elige el layout
    adecuado según el rol y estado de verificación del usuario.
    VERSIÓN CORREGIDA Y ROBUSTA.
    """
    if not isinstance(child, rx.Component):
        child = rx.heading("This is not a valid child element")

    verification_required_page = rx.center(
        rx.vstack(
            rx.heading("Verificación Requerida"),
            rx.text("Por favor, revisa tu correo para verificar tu cuenta."),
            spacing="4"
        ),
        height="80vh"
    )

    return rx.cond(
        SessionState.is_hydrated,
        # Si el usuario NO está autenticado, siempre muestra el layout público.
        rx.cond(
            ~SessionState.is_authenticated,
            public_layout(child),
            # Si SÍ está autenticado, ahora verificamos de forma segura.
            rx.cond(
                # Primero, nos aseguramos de que authenticated_user_info no sea nulo.
                SessionState.authenticated_user_info,
                # Si existe, comprobamos si está verificado.
                rx.cond(
                    SessionState.authenticated_user_info.is_verified,
                    # Usuario verificado: muestra el layout según su rol.
                    rx.cond(
                        SessionState.is_admin,
                        protected_layout(child),
                        public_layout(child)
                    ),
                    # Usuario NO verificado: muestra el mensaje de verificación.
                    public_layout(verification_required_page)
                ),
                # Caso raro: autenticado pero sin user_info, muestra layout público.
                public_layout(child)
            )
        ),
        # Muestra un spinner mientras carga el estado de la sesión.
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