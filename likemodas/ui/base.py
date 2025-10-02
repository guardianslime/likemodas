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
    """Estructura de página base con layout de admin y carga de datos de perfil."""
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
        # --- INICIO DE LA MEJORA DE CARGA DE DATOS ---
        # Al montar cualquier página de admin, se llama a on_load_profile_page
        # para asegurar que los datos del perfil (y el avatar) siempre estén disponibles.
        on_mount=rx.cond(AppState.is_admin, AppState.on_load_profile_page, None)
        # --- FIN DE LA MEJORA ---
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
            rx.cond(AppState.is_admin, admin_layout, public_layout)
        ),
        fixed_color_mode_button(),
    )