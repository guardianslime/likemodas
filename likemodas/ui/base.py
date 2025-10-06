import reflex as rx
from reflex.style import toggle_color_mode
from ..state import AppState
from .nav import public_navbar
from .sidebar import sliding_admin_sidebar

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
    [CORREGIDO] Estructura de página base que ahora diferencia entre 
    Admin/Vendedor y el resto de usuarios.
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
            # --- ¡ESTA ES LA CORRECCIÓN CLAVE! ---
            # Ahora se comprueba si el usuario es Admin O Vendedor.
            rx.cond(
                AppState.is_admin | AppState.is_vendedor, 
                admin_layout, 
                public_layout
            )
            # --- FIN DE LA CORRECCIÓN ---
        ),
        
        # El sistema de polling para la redirección automática (esto ya es correcto)
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
                            }, 10000); // Verifica cada 10 segundos
                        }
                        """
                    ),
                    display="none",
                )
            )
        ),
        
        fixed_color_mode_button(),
    )