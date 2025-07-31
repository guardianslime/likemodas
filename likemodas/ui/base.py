import reflex as rx
from reflex.components.component import NoSSRComponent
from ..auth.state import SessionState
from .nav import public_navbar
from .sidebar import sidebar

def fixed_color_mode_button() -> rx.Component:
    """Un botón de cambio de tema que se renderiza solo en el cliente."""
    return rx.box(
        rx.color_mode.button(),
        position="fixed",
        bottom="1.5rem",
        right="1.5rem",
        z_index="1000",
    )

def base_page(child: rx.Component, *args, **kwargs) -> rx.Component:
    """
    Función principal que envuelve todo el contenido y elige el layout
    adecuado, gestionando el estado de hidratación para evitar parpadeos.
    """
    if not isinstance(child, rx.Component):
        child = rx.heading("This is not a valid child element")

    # Página de advertencia para usuarios no verificados
    verification_required_page = rx.center(
        rx.vstack(
            rx.heading("Verificación Requerida"),
            rx.text("Por favor, revisa tu correo electrónico para verificar tu cuenta antes de continuar."),
            spacing="4"
        ),
        height="80vh"
    )

    # Contenido principal que se mostrará
    main_content = rx.cond(
        # Primero verifica si el usuario está autenticado y verificado
        (SessionState.is_authenticated & SessionState.authenticated_user_info.is_verified) | ~SessionState.is_authenticated,
        child,
        verification_required_page
    )

    # Layout unificado y responsivo
    unified_layout = rx.fragment(
        # El navbar superior siempre es visible para todos en el layout público/de cliente
        rx.cond(~SessionState.is_admin, public_navbar()),

        rx.hstack(
            # La barra lateral solo se muestra si es admin
            rx.cond(SessionState.is_admin, sidebar()),
            
            # El contenido principal de la página
            rx.box(
                main_content,
                padding="1em",
                # Ajuste responsivo del padding superior para el navbar fijo
                padding_top=rx.cond(~SessionState.is_admin, "6rem", "1em"),
                width="100%",
                id="my-content-area-el"
            ),
            align="start",
            width="100%"
        ),
        
        # El botón de modo oscuro solo para el layout público
        rx.cond(~SessionState.is_admin, fixed_color_mode_button())
    )

    return rx.cond(
        SessionState.is_hydrated,
        unified_layout,
        rx.center(rx.spinner(size="3"), height="100vh") # Esqueleto de carga inicial
    )