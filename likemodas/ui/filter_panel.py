# likemodas/ui/filter_panel.py

import reflex as rx
from .filter_state import FilterState

def floating_filter_panel() -> rx.Component:
    """
    Un panel de filtros flotante y deslizable desde la izquierda.
    """
    return rx.box(
        rx.hstack(
            # El contenido principal del panel de filtros
            rx.vstack(
                rx.heading("Filtros", size="6", width="100%"),
                rx.divider(),
                
                # Sección de filtros de Precio
                rx.vstack(
                    rx.text("Precio", weight="bold"),
                    rx.input(
                        placeholder="Mínimo",
                        value=FilterState.min_price,
                        on_change=FilterState.set_min_price,
                        type="number"
                    ),
                    rx.input(
                        placeholder="Máximo",
                        value=FilterState.max_price,
                        on_change=FilterState.set_max_price,
                        type="number"
                    ),
                    spacing="2",
                    align_items="start",
                    width="100%"
                ),
                
                # Aquí puedes añadir más filtros en el futuro (talla, color, etc.)
                
                spacing="4",
                padding="1.5em",
                bg=rx.color("gray", 2),
                height="100%",
                width="280px", # Ancho fijo del panel
            ),
            
            # La pestaña vertical para mostrar/ocultar el panel
            rx.box(
                rx.text(
                    "Filtros",
                    style={
                        "writing_mode": "vertical-rl",
                        "transform": "rotate(180deg)",
                        "padding": "1em 0.5em",
                        "font_weight": "bold",
                        "letter_spacing": "2px",
                        "color": "white"
                    }
                ),
                on_click=FilterState.toggle_filters,
                cursor="pointer",
                bg=rx.color("blue", 9),
                border_radius="0 8px 8px 0",
                height="120px",
                display="flex",
                align_items="center"
            ),
            align_items="center",
            spacing="0"
        ),
        position="fixed",
        top="50%", # Centrado verticalmente en la pantalla
        left="0",
        # Lógica de deslizamiento con transform
        transform=rx.cond(
            FilterState.show_filters,
            "translateY(-50%)", # Posición expandida
            "translate(-280px, -50%)" # Posición colapsada (ancho del panel)
        ),
        transition="transform 0.3s ease-in-out",
        z_index="1000", # Asegura que flote sobre otros elementos
        height="auto",
    )