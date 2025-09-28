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
    """
    Estructura de página base con un layout de admin basado en Grid para un
    centrado robusto y predecible.
    """
    loading_screen = rx.center(
        rx.spinner(size="3"),
        height="100vh",
        width="100%",
        background=rx.color("gray", 2)
    )

    # --- INICIO DE LA REESTRUCTURACIÓN ---
    admin_layout = rx.box(
        # La barra lateral se mantiene como una superposición
        sliding_admin_sidebar(),
        
        # Usamos una rejilla para el contenido principal
        rx.grid(
            # 1. Columna fantasma: un espacio vacío que empuja el contenido
            # para que no quede debajo del botón del menú lateral.
            rx.box(display=["none", "none", "block"]), # Oculto en móvil
            
            # 2. Columna principal: aquí irá el contenido de cada página (el 'child').
            # Ocupará todo el espacio restante.
            rx.box(
                child,
                width="100%",
                height="100%",
                padding_x=["1em", "2em"],
                padding_y="2em",
            ),
            
            # Definimos el comportamiento de las columnas.
            # En móvil: una sola columna.
            # En escritorio ('lg'): una columna de 5em y la otra ocupa el resto (1fr).
            columns={"initial": "1", "lg": "5em 1fr"},
            width="100%",
        ),
        width="100%",
        min_height="100vh",
    )
    # --- FIN DE LA REESTRUCTURACIÓN ---

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