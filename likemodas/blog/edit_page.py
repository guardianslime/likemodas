# likemodas/blog/edit_page.py (CORREGIDO)

import reflex as rx
from ..state import AppState

def _image_display_section() -> rx.Component:
    """Muestra las imágenes actuales de la publicación que se está editando."""
    return rx.vstack(
        rx.heading("Imágenes Actuales", size="5"),
        rx.text("Estas son las imágenes guardadas para esta publicación.", size="2", color_scheme="gray"),
        rx.cond(
            AppState.post.image_urls & (AppState.post.image_urls.length() > 0),
            rx.grid(
                rx.foreach(
                    AppState.post.image_urls,
                    lambda image_url: rx.box(
                        rx.image(
                            src=rx.get_upload_url(image_url), 
                            alt=AppState.post.title, 
                            width="100%", 
                            height="auto", 
                            object_fit="cover", 
                            border_radius="var(--radius-3)"
                        ),
                    )
                ),
                columns="3", spacing="4", width="100%", padding_top="1em"
            ),
            rx.box(
                rx.text("Esta publicación aún no tiene imágenes."),
                padding="2em",
                border="1px dashed",
                border_color=rx.color("gray", 6),
                border_radius="md",
                width="100%",
                text_align="center",
                margin_top="1em"
            )
        ),
        spacing="3",
        align_items="start",
        width="100%",
        padding="1.5em",
        border="1px solid",
        border_color=rx.color("gray", 4),
        border_radius="lg"
    )

def blog_post_edit_content() -> rx.Component:
    """Contenido de la página para editar una publicación existente."""
    # Envolvemos todo en rx.center para centrar el contenido vertical y horizontalmente.
    return rx.center(
        rx.container(
            rx.vstack(
                rx.heading("Editar Publicación", size="8"),
                rx.text("Modifica los detalles de tu producto y guárdalos."),
                rx.divider(margin_y="1.5em"),
                
                # Usamos un condicional para mostrar el contenido solo si el post está cargado
                rx.cond(
                    AppState.post,
                    rx.vstack(
                        # Nueva sección para mostrar las imágenes
                        _image_display_section(),
                        
                        # Formulario de edición
                        rx.form(
                            rx.vstack(
                                rx.text("Título del Producto", as_="div", size="2", margin_bottom="2px", weight="bold"),
                                rx.input(
                                    name="title", # Se añade el name
                                    value=AppState.post_title,
                                    on_change=AppState.set_post_title,
                                    placeholder="Ej: Camisa de Lino",
                                    width="100%"
                                ),
                                
                                rx.text("Descripción", as_="div", size="2", margin_bottom="2px", weight="bold"),
                                rx.text_area(
                                    name="content", # Se añade el name
                                    value=AppState.post_content,
                                    on_change=AppState.set_post_content,
                                    placeholder="Describe los detalles, materiales, etc.",
                                    width="100%",
                                    rows="8",
                                ),

                                rx.text("Precio (COP)", as_="div", size="2", margin_bottom="2px", weight="bold"),
                                rx.input(
                                    name="price", # Se añade el name
                                    value=AppState.price_str,
                                    on_change=AppState.set_price,
                                    placeholder="Ej: 80000",
                                    width="100%"
                                ),
                                
                                rx.button("Guardar Cambios", type="submit", width="100%", margin_top="1em", size="3"),
                                spacing="4",
                                width="100%"
                            ),
                            # Asegúrate de que el handler en AppState use los names del form
                            on_submit=AppState.handle_edit_submit,
                            width="100%",
                            margin_top="2em" # Espacio entre las imágenes y el form
                        ),
                        spacing="6",
                        width="100%",
                    ),
                    # Muestra un spinner mientras carga la información del post
                    rx.center(rx.spinner(), height="50vh")
                ),
                spacing="5",
                width="100%",
            ),
            padding_y="2em",
            max_width="900px", # Aumentamos un poco el ancho para dar espacio
        ),
        min_height="85vh",
        width="100%",
        padding="1em"
    )