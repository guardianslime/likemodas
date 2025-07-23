# likemodas/ui/filter_sidebar.py

import reflex as rx
from likemodas.states.gallery_state import ProductGalleryState

def filter_sidebar() -> rx.Component:
    """Un panel de filtros flotante que se activa con un botón en el borde."""
    return rx.fragment(
        # El botón de activación, ahora en el medio a la izquierda
        rx.icon_button(
            rx.icon("filter"),
            position="fixed",
            top="50%",
            left="1em",
            transform="translateY(-50%)",
            z_index="10",
            on_click=ProductGalleryState.toggle_filters,
            size="2"
        ),
        # El panel de filtros, que aparece y desaparece
        rx.cond(
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
                left="0",
                height="100vh",
                width="250px", # Ancho del panel
                padding="1em",
                bg=rx.color("gray", 2),
                z_index="20",
                border_right="1px solid",
                border_color=rx.color("gray", 5),
            )
        )
    )