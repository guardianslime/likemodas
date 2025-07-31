# -----------------------------------------------------------------------------
# likemodas/ui/base.py
# -----------------------------------------------------------------------------
import reflex as rx
# ✨ CAMBIO CLAVE: Se eliminan las importaciones de 'SessionState' y 'public_navbar' de la parte superior.
# from..auth.state import SessionState -> ELIMINADA
# from .nav import public_navbar -> ELIMINADA
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
    Layout base robusto que previene errores visuales por estados sin hidratar
    y mantiene la estructura del DOM estable.
    """
    # --- ✨ CAMBIO CLAVE ---
    # Se importan los módulos necesarios DENTRO de la función.
    # Esto rompe el ciclo de importación circular, ya que los módulos
    # solo se cargan cuando esta función es ejecutada, no cuando se carga `ui.base`.
    from ..auth.state import SessionState
    from .nav import public_navbar

    # Protege contra errores en el argumento
    if not isinstance(child, rx.Component):
        child = rx.heading("Error: El elemento hijo no es un componente válido")

    # Muestra mensaje si requiere verificación
    verification_required_page = rx.center(
        rx.vstack(
            rx.heading("Verificación Requerida"),
            rx.text("Por favor, revisa tu correo para verificar tu cuenta."),
            spacing="4"
        ),
        height="80vh"
    )

    # Página principal con verificación condicional
    main_content = rx.cond(
        (SessionState.is_authenticated & SessionState.authenticated_user_info.is_verified) | ~SessionState.is_authenticated,
        child,
        verification_required_page
    )

    # Estructura de layout unificado
    unified_layout = rx.hstack(
        # Sidebar solo para admins
        rx.cond(
            SessionState.is_admin,
            sidebar(),
            rx.fragment()
        ),
        rx.box(
            # Navbar solo para usuarios
            rx.cond(
                ~SessionState.is_admin,
                public_navbar(),
                rx.fragment()
            ),
            rx.box(
                main_content,
                padding_top=rx.cond(~SessionState.is_admin, "6rem", "1em"),
                padding_right="1em",
                padding_bottom="1em",
                padding_left="1em",
                width="100%",
            ),
            width="100%",
        ),
        # Botón de modo de color solo para usuarios
        rx.cond(
            ~SessionState.is_admin,
            fixed_color_mode_button(),
            rx.fragment()
        ),
        align="start",
        spacing="0",
        width="100%",
        min_height="100vh",
    )

    # Protege la estructura hasta que el estado esté hidratado
    return rx.cond(
        SessionState.is_hydrated,
        unified_layout,
        rx.center(rx.spinner(size="3"), height="100vh")
    )