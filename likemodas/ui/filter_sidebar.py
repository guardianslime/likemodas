# likemodas/ui/filter_sidebar.py

import reflex as rx
from likemodas.states.gallery_state import ProductGalleryState

def filter_panel() -> rx.Component:
    """Un panel de filtros que aparece y desaparece."""
    return rx.cond(
        ProductGalleryState.show_filters,
        rx.vstack(
            rx.hstack(
                rx.heading("Filtros"),
                rx.spacer(),
                rx.icon_button(
                    rx.icon("x"),
                    on_click=ProductGalleryState.toggle_filters,
                    variant="ghost"
                ),
                justify="between",
                width="100%"
            ),
            rx.divider(),
            rx.vstack(
                rx.text("Precio", weight="bold"),
                rx.hstack(
                    rx.input(
                        placeholder="Mínimo", 
                        value=ProductGalleryState.min_price,
                        on_change=ProductGalleryState.set_min_price
                    ),
                    rx.input(
                        placeholder="Máximo", 
                        value=ProductGalleryState.max_price,
                        on_change=ProductGalleryState.set_max_price
                    ),
                ),
                align_items="start",
                width="100%"
            ),
            spacing="5",
            position="fixed",
            top="0",
            left="16em",  # Se alinea a la derecha del sidebar principal
            height="100vh",
            width="220px", # <-- Ancho reducido como pediste
            padding="1em",
            bg=rx.color("accent", 2),
            z_index="10",
            border_right="1px solid",
            border_color=rx.color("gray", 5),
            transition="transform 0.3s ease",
            transform="translateX(0)",
        ),
    )