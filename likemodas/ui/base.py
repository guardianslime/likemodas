import reflex as rx
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

def debug_banner() -> rx.Component:
    """
    Un banner de depuración temporal para ver el estado en tiempo real.
    Se mostrará en la esquina inferior izquierda.
    """
    return rx.box(
        rx.hstack(
            rx.text("DEBUG:", weight="bold"),
            rx.text("is_hydrated:"),
            rx.text(SessionState.is_hydrated.to_string()),
            rx.text(" | is_authenticated:"),
            rx.text(SessionState.is_authenticated.to_string()),
            rx.text(" | is_admin:"),
            rx.text(SessionState.is_admin.to_string()),
            spacing="3",
        ),
        position="fixed",
        bottom="10px",
        left="10px",
        bg="rgba(220, 50, 50, 0.85)",
        color="white",
        padding="10px",
        border_radius="md",
        z_index=9999,
    )

def base_page(child: rx.Component, *args, **kwargs) -> rx.Component:
    """
    Función de layout base unificada y robusta que utiliza posicionamiento fijo
    y un banner de depuración para diagnosticar problemas de estado.
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

    main_content = rx.cond(
        (SessionState.is_authenticated & SessionState.authenticated_user_info.is_verified) | ~SessionState.is_authenticated,
        child,
        verification_required_page
    )

    # Layout unificado con posicionamiento explícito
    unified_layout = rx.box(
        # La barra lateral del ADMIN se posiciona a la izquierda
        rx.cond(
            SessionState.is_admin,
            rx.box(
                sidebar(),
                position="fixed",
                top="0px",
                left="0px",
                height="100%",
                z_index=50,
            )
        ),
        # El navbar PÚBLICO se posiciona arriba
        rx.cond(
            ~SessionState.is_admin,
            rx.box(
                public_navbar(),
                position="fixed",
                top="0px",
                left="0px",
                width="100%",
                z_index=50,
            )
        ),
        # El área de contenido principal con PADDING RESPONSIVO Y EXPLÍCITO
        rx.box(
            main_content,
            padding_left=rx.cond(
                SessionState.is_admin,
                rx.breakpoints(initial="0em", md="16em"), # Padding en escritorio si es admin
                "0em"                                     # Sin padding si es público
            ),
            padding_top=rx.cond(
                ~SessionState.is_admin,
                "6rem", # Padding para el navbar público
                "1em"
            ),
            padding_right="1em",
            padding_bottom="1em",
            width="100%",
        ),
        fixed_color_mode_button(),
        debug_banner(), # <-- AÑADIMOS EL BANNER DE DEPURACIÓN AQUÍ
    )

    return rx.cond(
        SessionState.is_hydrated,
        unified_layout,
        rx.center(rx.spinner(size="3"), height="100vh")
    )