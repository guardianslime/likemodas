import reflex as rx
from reflex.style import toggle_color_mode
from ..state import AppState
from .nav import public_navbar  # Importa la nueva navbar de prueba
from .skeletons import skeleton_navbar
from .sidebar import sidebar, mobile_admin_menu, sidebar_dark_mode_toggle_item

def fixed_color_mode_button() -> rx.Component:
    """Botón flotante para cambiar el modo de color."""
    return rx.box(
        rx.button(
            rx.color_mode_cond(
                light=rx.icon(tag="sun"), 
                dark=rx.icon(tag="moon")
            ),
            on_click=toggle_color_mode,
            variant="soft",
            radius="full"
        ),
        position="fixed", bottom="1.5rem", right="1.5rem", z_index="1000",
    )

def public_layout(child: rx.Component) -> rx.Component:
    """El layout para las páginas públicas, ahora con la navbar de prueba."""
    return rx.box(
        public_navbar(),  # <-- Usando la navbar segura
        rx.box(
            child,
            padding_top="6rem",
            padding_x="1em",
            padding_bottom="1em",
            width="100%",
        ),
        fixed_color_mode_button(),
        width="100%",
    )

def admin_layout(child: rx.Component) -> rx.Component:
    """El layout para las páginas de administración."""
    return rx.fragment(
        rx.box(
            rx.vstack(
                rx.hstack(
                    mobile_admin_menu(), rx.spacer(),
                    rx.image(src="/logo.png", width="6em", height="auto"),
                    rx.spacer(), sidebar_dark_mode_toggle_item(),
                    width="100%", padding="0.5em 1em", bg="#2C004B", align="center",
                ),
                rx.box(child, padding="1em", width="100%"),
                display=["flex", "flex", "none", "none", "none"], spacing="0",
            ),
        ),
        rx.hstack(
            sidebar(),
            rx.box(child, padding="1em", width="100%"),
            display=["none", "none", "flex", "flex", "flex"],
            align="start", spacing="0", width="100%", min_height="100vh",
        ),
    )

def base_page(child: rx.Component, *args, **kwargs) -> rx.Component:
    """La página base que aplica el layout correcto."""
    return rx.cond(
        ~AppState.is_hydrated,
        # Layout Esqueleto (Funciona como antes)
        rx.box(
            skeleton_navbar(),
            rx.box(
                child,
                padding_top="6rem", padding_x="1em", padding_bottom="1em", width="100%"
            ),
            width="100%",
        ),
        # Layout Real (Ahora usa los componentes de layout seguros)
        rx.match(
            AppState.is_admin,
            (True, admin_layout(child)),
            (False, public_layout(child)),
            public_layout(child),
        ),
    )