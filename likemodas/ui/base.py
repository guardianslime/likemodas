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

def base_page(child: rx.Component, *args, **kwargs) -> rx.Component:
    """
    Función de layout final que renderiza vistas completamente separadas para
    admin y cliente para evitar bugs de renderizado condicional de estilos.
    """
    if not isinstance(child, rx.Component):
        child = rx.heading("This is not a valid child element")

    # Contenido principal (lógica de verificación sin cambios)
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

    # --- NUEVA LÓGICA DE VISTAS SEPARADAS ---

    # VISTA PARA EL ADMINISTRADOR
    admin_view = rx.hstack(
        sidebar(),
        rx.box(
            main_content,
            padding="1em",
            width="100%",
        ),
        align="start",
        spacing="0",
        width="100%",
    )

    # VISTA PARA EL CLIENTE PÚBLICO
    customer_view = rx.box(
        public_navbar(),
        rx.box(
            main_content,
            padding_top="6rem",
            padding_right="1em",
            padding_bottom="1em",
            padding_left="1em",
            width="100%",
        ),
        fixed_color_mode_button(),
    )

    # El rx.cond principal ahora elige entre las dos vistas completas
    unified_layout = rx.cond(
        SessionState.is_admin,
        admin_view,
        customer_view
    )

    return rx.cond(
        SessionState.is_hydrated,
        unified_layout,
        rx.center(rx.spinner(size="3"), height="100vh")
    )