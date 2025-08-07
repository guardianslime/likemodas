# likemodas/pages/admin.py

import reflex as rx
from likemodas.state import AppState
from likemodas.components.navbar import navbar

def admin_page() -> rx.Component:
    """Página de administración para crear productos."""
    return rx.box(
        navbar(),
        rx.container(
            rx.heading("Crear Nuevo Producto", size="8", margin_top="3em"),
            rx.form(
                rx.vstack(
                    rx.input(name="title", placeholder="Nombre del Producto", required=True),
                    rx.text_area(name="content", placeholder="Descripción del Producto", required=True),
                    rx.input(name="price", placeholder="Precio (ej: 50000)", type="number", required=True),
                    
                    # Sección de subida de imágenes
                    rx.upload(
                        rx.text("Arrastra o haz clic para subir imágenes"),
                        id="upload-images",
                        multiple=True,
                        border="2px dashed #ccc",
                        padding="2em",
                    ),
                    rx.button(
                        "Procesar Imágenes",
                        on_click=AppState.handle_upload(rx.upload_files(upload_id="upload-images")),
                        is_loading=AppState.is_uploading,
                        margin_top="1em",
                    ),
                    
                    # Previsualización de imágenes subidas
                    rx.hstack(
                        rx.foreach(
                            AppState.temp_images,
                            lambda img: rx.box(
                                rx.image(src=rx.get_upload_url(img), height="5em", width="auto"),
                                rx.icon(
                                    tag="trash",
                                    on_click=lambda: AppState.remove_temp_image(img),
                                    position="absolute",
                                    top="2px",
                                    right="2px",
                                    cursor="pointer",
                                    color="red",
                                ),
                                position="relative",
                            )
                        ),
                        wrap="wrap",
                        margin_top="1em",
                    ),
                    
                    rx.button("Guardar Producto", type="submit", margin_top="1em"),
                    spacing="4",
                ),
                on_submit=AppState.create_product,
                id="form-create-product", # ID para poder resetearlo desde el estado
            ),
            padding_top="5em",
            max_width="800px",
        )
    )