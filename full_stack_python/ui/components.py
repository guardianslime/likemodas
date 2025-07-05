# full_stack_python/ui/components.py

import reflex as rx

def not_found_component(title: str = "Página no encontrada", text: str = "El contenido que buscas no existe.") -> rx.Component:
    """Un componente genérico para mostrar un mensaje de 'No Encontrado'."""
    return rx.vstack(
        rx.heading(title, size="9"),
        rx.text(text),
        rx.link(
            "Volver al Inicio",
            href="/",
            button=True,
            color_scheme="gray",
        ),
        spacing="5",
        justify="center",
        align="center",
        min_height="85vh",
    )