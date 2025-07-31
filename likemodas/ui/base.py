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
    Función de layout base unificada y robusta que utiliza posicionamiento fijo
    para evitar saltos de layout y problemas de renderizado.
    """
    if not isinstance(child, rx.Component):
        child = rx.heading("This is not a valid child element")

    # Página de advertencia para usuarios no verificados
    verification_required_page = rx.center(
        rx.vstack(
            rx.heading("Verificación Requerida"),
            rx.text("Por favor, revisa tu correo para verificar tu cuenta."),
            spacing="4"
        ),
        height="80vh"
    )

    # Contenido principal que se mostrará
    main_content = rx.cond(
        (SessionState.is_authenticated & SessionState.authenticated_user_info.is_verified) | ~SessionState.is_authenticated,
        child,
        verification_required_page
    )

    # Layout unificado y responsivo con posicionamiento
    unified_layout = rx.box(
        # La barra lateral del ADMIN se renderiza condicionalmente y se posiciona a la izquierda
        rx.cond(
            SessionState.is_admin,
            rx.box(
                sidebar(),  # El componente sidebar ya maneja su vista móvil/escritorio
                position="fixed",
                top="0px",
                left="0px",
                height="100%",
                z_index=50,
            )
        ),

        # El navbar PÚBLICO se renderiza condicionalmente y se posiciona arriba
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

        # El área de contenido principal con PADDING RESPONSIVO
        rx.box(
            main_content,
            # Se añade padding a la izquierda en ESCRITORIO si el usuario es ADMIN
            padding_left=rx.cond(
                SessionState.is_admin,
                ["0em", "0em", "16em", "16em"],  # 16em es el ancho de la sidebar
                "0em"
            ),
            # Se añade padding arriba si el usuario es PÚBLICO para no tapar con el navbar
            padding_top=rx.cond(
                ~SessionState.is_admin,
                "6rem", # Altura del navbar
                "1em"
            ),
            padding_right="1em",
            padding_bottom="1em",
            width="100%",
        ),

        # Botón de modo oscuro para usuarios PÚBLICOS
        rx.cond(
            ~SessionState.is_admin,
            fixed_color_mode_button(),
        ),
    )

    # Lógica de carga para evitar mostrar contenido antes de la hidratación
    return rx.cond(
        SessionState.is_hydrated,
        unified_layout,
        rx.center(rx.spinner(size="3"), height="100vh")
    )