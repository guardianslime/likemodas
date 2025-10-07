# likemodas/ui/base.py

import reflex as rx
from reflex.style import toggle_color_mode
from ..state import AppState
from .nav import public_navbar
from .sidebar import sliding_admin_sidebar

# --- ✨ INICIO: NUEVO BANNER PERSONALIZADO ✨ ---
def persistent_employment_request_banner() -> rx.Component:
    """
    Un banner personalizado y persistente que flota en la parte superior derecha
    y muestra una solicitud de empleo pendiente con opciones para aceptar o rechazar.
    Funciona en versiones antiguas de Reflex.
    """
    return rx.box(
        # Usamos rx.cond para mostrar el banner solo si hay una notificación pendiente
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
                # Estilos del banner
                padding="1em",
                width="100%",
                max_width="450px",
            ),
        ),
        # Estilos para posicionar el banner
        position="fixed",
        top="7rem", # Lo ubicamos debajo de la barra de navegación
        right="1.5rem",
        z_index="1500", # Un z-index alto para que flote sobre todo
        transition="transform 0.5s ease-in-out, opacity 0.5s", # Animación suave
        # Controlamos la animación con transform y opacity
        transform=rx.cond(
            AppState.pending_request_notification,
            "translateY(0)", # Posición visible
            "translateY(-20px)" # Posición oculta (ligeramente arriba)
        ),
        opacity=rx.cond(AppState.pending_request_notification, "1", "0"),
        pointer_events=rx.cond(AppState.pending_request_notification, "auto", "none"),
    )
# --- ✨ FIN: NUEVO BANNER PERSONALIZADO ✨ ---

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
    [CORREGIDO] Estructura de página base que ahora muestra el panel de admin
    a Vendedores, Administradores y Empleados.
    """
    loading_screen = rx.center(rx.spinner(size="3"), height="100vh", width="100%", background=rx.color("gray", 2))

    admin_layout = rx.box(
        sliding_admin_sidebar(),
        rx.grid(
            rx.box(display=["none", "none", "block"]),
            rx.box(child, width="100%", height="100%", padding_x=["1em", "2em"], padding_y="2em"),
            columns={"initial": "1", "lg": "5em 1fr"},
            width="100%",
        ),
        width="100%",
        min_height="100vh",
        on_mount=rx.cond(AppState.is_admin, AppState.on_load_profile_page, None)
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
            # --- ✨ ¡ESTA ES LA CORRECCIÓN CLAVE! ✨ ---
            # Se añade AppState.is_empleado a la condición
            rx.cond(
                AppState.is_admin | AppState.is_vendedor | AppState.is_empleado, 
                admin_layout, 
                public_layout
            )
        ),
        
        # Polling para el rol de usuario (se mantiene igual)
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
        
        # --- ✨ INICIO: SE AÑADEN EL BANNER Y SU MECANISMO DE ACTIVACIÓN ✨ ---
        rx.cond(
            AppState.is_vendedor | AppState.is_admin,
            rx.fragment(
                # Botón oculto que se activa periódicamente
                rx.button(
                    "Employment Polling Trigger",
                    on_click=AppState.poll_employment_requests,
                    id="employment_poller_button",
                    display="none",
                ),
                # Script que activa el botón
                rx.box(
                    on_mount=rx.call_script(
                        """
                        if (!window.likemodas_employment_poller) {
                            window.likemodas_employment_poller = setInterval(() => {
                                const trigger = document.getElementById('employment_poller_button');
                                if (trigger) {
                                    trigger.click();
                                }
                            }, 12000);
                        }
                        """
                    ),
                    display="none",
                )
            )
        ),
        
        # El componente del banner que acabamos de crear
        persistent_employment_request_banner(),
        # --- ✨ FIN: NUEVO BLOQUE ✨ ---
        
        fixed_color_mode_button(),
    )