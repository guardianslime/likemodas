import reflex as rx
from ..auth.state import SessionState
from .nav import public_navbar 
from .sidebar import sidebar

def fixed_color_mode_button() -> rx.Component:
    return rx.box(
        rx.color_mode.button(),
        position="fixed", bottom="1.5rem", right="1.5rem", z_index="100",
    )

def protected_layout(child: rx.Component) -> rx.Component:
    return rx.hstack(
        sidebar(),
        rx.box(child, padding="1em", width="100%", id="my-content-area-el"),
        align="start"
    )

def public_layout(child: rx.Component) -> rx.Component:
    return rx.fragment(
        public_navbar(),
        rx.box(child, padding="1em", padding_top="6rem", width="100%", id="my-content-area-el"),
        fixed_color_mode_button()
    )

def base_page(child: rx.Component, *args, **kwargs) -> rx.Component:
    """
    Función principal que envuelve TODO el contenido, aplica el TEMA
    y maneja la lógica de autenticación de forma segura.
    """
    verification_required_page = rx.center(
        rx.vstack(
            rx.heading("Verificación Requerida"),
            rx.text("Por favor, revisa tu correo para verificar tu cuenta."),
            spacing="4"
        ),
        height="80vh"
    )

    page_content = rx.cond(
        SessionState.is_hydrated,
        rx.cond(
            ~SessionState.is_authenticated,
            public_layout(child),
            rx.cond(
                SessionState.authenticated_user_info & SessionState.authenticated_user_info.is_verified,
                rx.cond(
                    SessionState.is_admin,
                    protected_layout(child),
                    public_layout(child)
                ),
                public_layout(verification_required_page)
            )
        ),
        rx.center(rx.spinner(), height="100vh")
    )

    # Se envuelve todo en el tema para garantizar que los estilos SIEMPRE se apliquen.
    return rx.theme(
        page_content,
        appearance="dark",
        has_background=True,
        panel_background="solid",
        scaling="90%",
        radius="medium",
        accent_color="sky"
    )