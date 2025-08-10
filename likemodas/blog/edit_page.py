# likemodas/blog/edit_page.py (NUEVO ARCHIVO)

import reflex as rx
from ..state import AppState

def blog_post_edit_content() -> rx.Component:
    """Contenido de la página para editar una publicación existente."""
    return rx.container(
        rx.vstack(
            rx.heading("Editar Publicación", size="7"),
            rx.text("Modifica los detalles de tu producto y guárdalos."),
            rx.divider(margin_y="1.5em"),
            
            # Formulario de edición
            rx.form(
                rx.vstack(
                    rx.text("Título del Producto", as_="div", size="2", margin_bottom="2px", weight="bold"),
                    rx.input(
                        value=AppState.post_title,
                        on_change=AppState.set_post_title,
                        placeholder="Ej: Camisa de Lino",
                        width="100%"
                    ),
                    
                    rx.text("Descripción", as_="div", size="2", margin_bottom="2px", weight="bold"),
                    rx.text_area(
                        value=AppState.post_content,
                        on_change=AppState.set_post_content,
                        placeholder="Describe los detalles, materiales, etc.",
                        width="100%",
                        rows=8,
                    ),

                    rx.text("Precio (COP)", as_="div", size="2", margin_bottom="2px", weight="bold"),
                    rx.input(
                        value=AppState.price_str,
                        on_change=AppState.set_price,
                        placeholder="Ej: 80000",
                        width="100%"
                    ),
                    
                    rx.button("Guardar Cambios", type="submit", width="100%", margin_top="1em"),
                    spacing="4",
                    width="100%"
                ),
                on_submit=AppState.handle_edit_submit,
                width="100%"
            ),
            spacing="5",
            width="100%",
        ),
        padding_y="2em",
        max_width="800px", # Un contenedor más pequeño para el formulario
    )