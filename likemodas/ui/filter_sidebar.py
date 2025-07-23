# likemodas/ui/filter_sidebar.py

import reflex as rx
from likemodas.states.gallery_state import ProductGalleryState

def filter_sidebar() -> rx.Component:
    """Un sidebar flotante y desplegable para los filtros de productos."""
    return rx.drawer.root(
        rx.drawer.trigger(
            # Este es el botón flotante que el usuario verá
            rx.icon_button(
                rx.icon("filter"),
                position="fixed",
                top="100px",
                left="1em",
                z_index="10",
                on_click=ProductGalleryState.toggle_filters,
                size="3"
            )
        ),
        rx.drawer.overlay(z_index="15"),
        rx.drawer.portal(
            rx.drawer.content(
                rx.vstack(
                    rx.hstack(
                        rx.heading("Filtros"),
                        rx.drawer.close(rx.icon("x")),
                        justify="between",
                        width="100%"
                    ),
                    rx.divider(),
                    
                    # Filtro de Precio
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
                    padding="1em",
                ),
                top="auto",
                right="auto",
                height="100%",
                width="20em",
                bg=rx.color("gray", 2),
                z_index="20",
            )
        ),
        direction="left",
    )