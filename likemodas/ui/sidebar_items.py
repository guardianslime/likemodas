# my_app/ui/sidebar_items.py

import reflex as rx
from reflex.style import toggle_color_mode # Importar el manejador de eventos

def sidebar_dark_mode_toggle_item() -> rx.Component:
    """
    Un componente que muestra un botón para alternar el modo de color.
    """
    return rx.button(
        "Alternar Modo",
        on_click=toggle_color_mode,
        width="100%"
    )
