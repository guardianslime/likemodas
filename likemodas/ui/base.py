# likemodas/ui/base.py (VERSIÓN CORREGIDA Y ROBUSTA)

import reflex as rx
from reflex.components.component import NoSSRComponent
from..auth.state import SessionState
from.nav import public_navbar 
from.sidebar import sidebar

def fixed_color_mode_button() -> rx.Component:
    """Un botón de cambio de tema que no se renderiza en el servidor para evitar FOUC."""
    # NoSSRComponent evita el renderizado en el servidor.
    return NoSSRComponent.create(
        rx.box(
            rx.color_mode.button(),
            position="fixed",
            bottom="1.5rem",
            right="1.5rem",
            z_index="1000",
        )
    )

def protected_layout(child: rx.Component) -> rx.Component:
    """El layout para usuarios administradores autenticados."""
    return rx.hstack(
        sidebar(),
        rx.box(
            child,
            padding="1em",
            width="100%",
            id="my-content-area-el"
        ),
        align="start"
    )

def public_layout(child: rx.Component) -> rx.Component:
    """El layout para usuarios no autenticados y clientes."""
    return rx.fragment(
        public_navbar(),
        rx.box(
            child,
            padding="1em",
            padding_top="6rem", 
            width="100%",
            id="my-content-area-el"
        ),
        rx.cond(
            SessionState.is_hydrated,
            fixed_color_mode_button() # Renderizar el botón SÓLO DESPUÉS de la hidratación
        )
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

    # Lógica de renderizado condicional principal
    return rx.cond(
        SessionState.is_hydrated,
        # Si el estado está hidratado, procede con la lógica de autenticación y rol
        rx.cond(
            ~SessionState.is_authenticated,
            # 1. Usuario NO autenticado: layout público.
            public_layout(child),
            # 2. Usuario SÍ autenticado: verificar rol y estado de verificación.
            rx.cond(
                SessionState.is_admin,
                # 2a. Es ADMIN: layout protegido.
                protected_layout(
                    rx.cond(
                        SessionState.authenticated_user_info.is_verified,
                        child, # Si está verificado, muestra el contenido.
                        verification_required_page # Si no, muestra la advertencia.
                    )
                ),
                # 2b. Es CLIENTE: layout público.
                public_layout(
                    rx.cond(
                        SessionState.authenticated_user_info.is_verified,
                        child, # Si está verificado, muestra el contenido.
                        verification_required_page # Si no, muestra la advertencia.
                    )
                )
            )
        ),
        # Si el estado NO está hidratado, muestra un spinner de carga.
        rx.center(rx.spinner(size="3"), height="100vh")
    )