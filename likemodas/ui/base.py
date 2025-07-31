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
    Layout base unificado que previene desajustes de hidratación al usar
    una estructura DOM consistente y aplicar condicionales en componentes internos.
    """
    if not isinstance(child, rx.Component):
        child = rx.heading("Error: El elemento hijo no es un componente válido")

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

    # --- LÓGICA DE LAYOUT UNIFICADO (LA SOLUCIÓN CLAVE) ---
    unified_layout = rx.hstack(
        # 1. La barra lateral del admin o un fragmento vacío para el cliente.
        #    Esto mantiene la estructura hstack pero no renderiza nada visible para el cliente.
        rx.cond(
            SessionState.is_admin,
            sidebar(),
            rx.fragment() # Devuelve un nodo vacío, no afecta el DOM.
        ),
        # 2. Contenedor principal para el contenido de la página.
        rx.box(
            # 3. La navbar pública o un fragmento vacío para el admin.
            rx.cond(
                ~SessionState.is_admin,
                public_navbar(),
                rx.fragment()
            ),
            # 4. El contenido principal de la página.
            rx.box(
                main_content,
                # El padding se ajusta condicionalmente para el cliente.
                padding_top=rx.cond(~SessionState.is_admin, "6rem", "1em"),
                padding_right="1em",
                padding_bottom="1em",
                padding_left="1em",
                width="100%",
            ),
            width="100%",
        ),
        # 5. Botón de modo de color solo para clientes.
        rx.cond(
            ~SessionState.is_admin,
            fixed_color_mode_button(),
            rx.fragment()
        ),
        align="start",
        spacing="0",
        width="100%",
    )

    # 6. El condicional final solo muestra un spinner mientras el estado se hidrata.
    return rx.cond(
        SessionState.is_hydrated,
        unified_layout,
        rx.center(rx.spinner(size="3"), height="100vh")
    )