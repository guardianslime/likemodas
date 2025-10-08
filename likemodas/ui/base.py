# likemodas/ui/base.py

import reflex as rx
from reflex.style import toggle_color_mode
from ..state import AppState
from .nav import public_navbar
from .sidebar import sliding_admin_sidebar
from .admin_nav import admin_top_bar

def persistent_employment_request_banner() -> rx.Component:
    """
    Un banner personalizado y persistente que flota en la parte superior
    y muestra una solicitud de empleo pendiente con opciones para aceptar o rechazar.
    """
    return rx.box(
        rx.cond(
            AppState.pending_request_notification,
            rx.card(
                rx.hstack(
                    rx.icon("user-plus", size=24),
                    rx.vstack(
                        rx.text("¡Nueva solicitud de empleo!", weight="bold"),
                        rx.text(
                            "De: " + AppState.pending_request_notification.requester_username,
                            size="2"
                        ),
                        align_items="start",
                        spacing="0"
                    ),
                    rx.spacer(),
                    rx.hstack(
                        rx.button(
                            "Rechazar",
                            size="1",
                            color_scheme="red",
                            variant="soft",
                            on_click=AppState.responder_solicitud_empleo(AppState.pending_request_notification.id, False)
                        ),
                        rx.button(
                            "Aceptar",
                            size="1",
                            color_scheme="green",
                            on_click=AppState.responder_solicitud_empleo(AppState.pending_request_notification.id, True)
                        ),
                    ),
                    spacing="4",
                    align="center",
                    width="100%",
                ),
                padding="1em",
                width="100%",
                max_width="450px",
            ),
        ),
        position="fixed",
        top="7rem", # Lo bajamos un poco para que no choque con la nueva campana
        right="1.5rem",
        z_index="1500",
        transition="transform 0.5s ease-in-out, opacity 0.5s",
        transform=rx.cond(AppState.pending_request_notification, "translateY(0)", "translateY(-20px)"),
        opacity=rx.cond(AppState.pending_request_notification, "1", "0"),
        pointer_events=rx.cond(AppState.pending_request_notification, "auto", "none"),
    )

def fixed_color_mode_button() -> rx.Component:
    """Botón flotante para cambiar el modo de color."""
    return rx.box(
        rx.button(
            rx.color_mode_cond(light=rx.icon(tag="sun"), dark=rx.icon(tag="moon")),
            on_click=toggle_color_mode,
            variant="soft", radius="full", color_scheme="violet"
        ),
        position="fixed", bottom="1.5rem", right="1.5rem", z_index="1000",
    )

def base_page(child: rx.Component, *args, **kwargs) -> rx.Component:
    """
    Estructura de página base que ahora incluye el banner y el activador para las solicitudes.
    """
    loading_screen = rx.center(rx.spinner(size="3"), height="100vh", width="100%", background=rx.color("gray", 2))

    # --- ✨ REEMPLAZA LA VARIABLE admin_layout POR ESTA VERSIÓN ✨ ---
    admin_layout = rx.box(
        sliding_admin_sidebar(),
        rx.grid(
            rx.box(display=["none", "none", "block"]),  # Espaciador

            # ANTES: Aquí había un rx.vstack que contenía admin_top_bar()
            # AHORA: Dejamos solo el contenido principal de la página.
            rx.box(child, width="100%", height="100%", padding_x=["1em", "2em"], padding_y="2em"),

            columns={"initial": "1", "lg": "5em 1fr"},
            width="100%",
        ),
        width="100%",
        min_height="100vh",
    )

    public_layout = rx.box(
        public_navbar(),
        rx.box(child, padding_top="6rem", padding_x="1em", padding_bottom="1em", width="100%"),
        width="100%",
    )

    return rx.box(
        rx.cond(
            ~AppState.is_hydrated,
            loading_screen,
            rx.cond(
                AppState.is_admin | AppState.is_vendedor | AppState.is_empleado, 
                admin_layout, 
                public_layout
            )
        ),
        
        rx.cond(
            AppState.is_authenticated & ~AppState.is_admin,
            rx.fragment(
                rx.button(
                    "Role Polling Trigger",
                    on_click=AppState.poll_user_role,
                    id="role_poller_button",
                    display="none",
                ),
                rx.box(
                    on_mount=rx.call_script(
                        """
                        if (!window.likemodas_role_poller) {
                            window.likemodas_role_poller = setInterval(() => {
                                const trigger = document.getElementById('role_poller_button');
                                if (trigger) {
                                    trigger.click();
                                }
                            }, 10000);
                        }
                        """
                    ),
                    display="none",
                )
            )
        ),
        # --- ✨ INICIO: AÑADE ESTE BLOQUE AQUÍ ✨ ---
        # Añadimos la campana flotante del vendedor, con una condición
        # para que solo se muestre si el usuario está en el panel.
        rx.cond(
            AppState.is_admin | AppState.is_vendedor | AppState.is_empleado,
            admin_top_bar()
        ),
        # --- ✨ FIN DEL BLOQUE ✨ ---
        persistent_employment_request_banner(),

        fixed_color_mode_button(),
    )