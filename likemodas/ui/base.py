# likemodas/ui/base.py (VERSIÓN CON LAYOUT DE ADMIN CORREGIDO)

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

    # El layout del admin ahora usa un hstack para posicionar correctamente el contenido
    # al lado del espacio reservado por el menú lateral.
    admin_layout = rx.hstack(
        # Este componente no cambia, sigue siendo el menú deslizable
        sliding_admin_sidebar(),
        # --- ÁREA DE CONTENIDO PRINCIPAL CORREGIDA ---
        # Este es el "lienzo" donde se dibujarán todas las páginas del admin.
        # Ahora ocupa todo el ancho restante y puede centrar su contenido.
        rx.box(
            child,
            width="100%",
            height="100%",
            padding_x=["1em", "2em", "3em"],
            padding_y="2em",
        ),
        # Se añade un espaciado inicial para el menú colapsado
        spacing="0",
        padding_left=["0em", "0em", "4em"],
        width="100%",
        min_height="100vh",
        align="start",
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
        # El botón de modo oscuro se aplica a ambos layouts desde aquí
        fixed_color_mode_button(),
    )