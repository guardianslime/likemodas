# likemodas/ui/gallery_header.py

import reflex as rx

def gallery_header() -> rx.Component:
    """
    Un encabezado reutilizable para las páginas de galería,
    que incluye el popover de Categorías.
    """
    return rx.hstack(
        rx.popover.root(
            rx.popover.trigger(
                rx.button(
                    "Categorías", 
                    variant="outline", size="3", color="white",
                    border_radius="full", style={"border_color": "white"},
                )
            ),
            rx.popover.content(
                rx.hstack(
                    rx.button("Ropa", on_click=rx.redirect("/category/ropa"), variant="soft"),
                    rx.button("Calzado", on_click=rx.redirect("/category/calzado"), variant="soft"),
                    rx.button("Mochilas", on_click=rx.redirect("/category/mochilas"), variant="soft"),
                    rx.button("Ver Todo", on_click=rx.redirect("/"), variant="soft"),
                    spacing="3",
                ),
                padding="0.5em",
                side="right",
                align="center",
            ),
        ),
        justify="start",
        width="100%",
        max_width="1800px",
        padding_bottom="1em",
    )