# likemodas/ui/filter_panel.py

import reflex as rx
from .filter_state import FilterState
from ..auth.state import SessionState # <-- CAMBIA LA IMPORTACIÓN

def floating_filter_panel() -> rx.Component:
    """
    Un panel de filtros flotante y deslizable desde la izquierda.
    """
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.heading("Filtros", size="6", width="100%"),
                rx.divider(),
                rx.vstack(
                    rx.text("Precio", weight="bold"),
                    rx.input(
                        placeholder="Mínimo",
                        value=SessionState.min_price, # <-- CAMBIO
                        on_change=SessionState.set_min_price, # <-- CAMBIO
                        type="number"
                    ),
                    rx.input(
                        placeholder="Máximo",
                        value=SessionState.max_price, # <-- CAMBIO
                        on_change=SessionState.set_max_price, # <-- CAMBIO
                        type="number"
                    ),
                    spacing="2",
                    align_items="start",
                    width="100%"
                ),
                spacing="4",
                padding="1.5em",
                bg=rx.color("gray", 2),
                height="100%",
                width="280px",
            ),
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
                on_click=SessionState.toggle_filters, # <-- CAMBIO
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
        top="50%",
        left="0",
        transform=rx.cond(
            SessionState.show_filters, # <-- CAMBIO
            "translateY(-50%)",
            "translate(-280px, -50%)"
        ),
        transition="transform 0.3s ease-in-out",
        z_index="1000",
        height="auto",
    )