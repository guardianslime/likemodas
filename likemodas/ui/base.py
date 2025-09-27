# likemodas/ui/base.py (VERSIÓN CON LAYOUT DE ADMIN ESTRUCTURALMENTE CORREGIDO)

import reflex as rx
from reflex.style import toggle_color_mode
from ..state import AppState
from .nav import public_navbar
from .sidebar import sliding_admin_sidebar

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
            radius="full",
            color_scheme="violet"
        ),
        position="fixed", bottom="1.5rem", right="1.5rem", z_index="1000",
    )

def base_page(child: rx.Component, *args, **kwargs) -> rx.Component:
    """Estructura de página base con el layout de admin corregido para permitir un centrado real."""
    loading_screen = rx.center(
        rx.spinner(size="3"),
        height="100vh",
        width="100%",
        background=rx.color("gray", 2)
    )

    # El layout del admin ahora es un simple rx.box que sirve como fondo
    admin_layout = rx.box(
        # El menú lateral se superpone (position="fixed")
        sliding_admin_sidebar(),
        
        # --- ÁREA DE CONTENIDO PRINCIPAL CORREGIDA ---
        # Este es el "lienzo" donde se dibujarán todas las páginas del admin.
        # Le aplicamos un padding a la izquierda para que NUNCA se oculte debajo del menú.
        rx.box(
            child,
            width="100%",
            height="100%",
            padding_left=["1em", "2em", "5em"], # Padding izquierdo responsivo
            padding_right=["1em", "2em", "2em"],# Padding derecho responsivo
            padding_y="2em",
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
                AppState.is_admin,
                admin_layout,
                public_layout
            )
        ),
        fixed_color_mode_button(),
    )