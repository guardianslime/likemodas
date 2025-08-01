# -----------------------------------------------------------------------------
# likemodas/ui/base.py
# -----------------------------------------------------------------------------
import reflex as rx
from .sidebar import sidebar

def fixed_color_mode_button() -> rx.Component:
    return rx.box(
        rx.color_mode.button(),
        position="fixed", bottom="1.5rem", right="1.5rem", z_index="1000",
    )

def base_page(child: rx.Component, *args, **kwargs) -> rx.Component:
    from ..auth.state import SessionState
    from .nav import public_navbar

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

    unified_layout = rx.hstack(
        rx.cond(SessionState.is_admin, sidebar(), rx.fragment()),
        rx.box(
            rx.cond(~SessionState.is_admin, public_navbar(), rx.fragment()),
            rx.box(
                main_content,
                padding_top=rx.cond(~SessionState.is_admin, "6rem", "1em"),
                padding_right="1em", padding_bottom="1em", padding_left="1em",
                width="100%",
            ),
            width="100%",
        ),
        rx.cond(~SessionState.is_admin, fixed_color_mode_button(), rx.fragment()),
        align="start", spacing="0", width="100%", min_height="100vh",
    )

    return rx.cond(
        SessionState.is_hydrated,
        unified_layout,
        rx.center(rx.spinner(size="3"), height="100vh")
    )