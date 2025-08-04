# likemodas/ui/base.py

import reflex as rx
from..auth.state import SessionState
from.nav import public_navbar
from.sidebar import sidebar

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

    # ✅ Layout para administradores
    admin_layout = rx.hstack(
        sidebar(),
        rx.box(
            main_content,
            padding="1em",
            width="100%",
        ),
        align="start",
        spacing="0",
        width="100%",
        min_height="100vh",
    )

    # ✅ Layout para usuarios públicos y clientes
    public_layout = rx.box(
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
        width="100%",
    )

    # 🛡️ CAMBIO CLAVE: Se decide qué layout mostrar DESPUÉS de la hidratación.
    # Esto previene el "salto" de la interfaz.
    return rx.cond(
        SessionState.is_hydrated,
        rx.cond(
            SessionState.is_admin,
            admin_layout,
            public_layout
        ),
        # Muestra un spinner global mientras se carga el estado inicial.
        rx.center(rx.spinner(size="3"), height="100vh")
    )