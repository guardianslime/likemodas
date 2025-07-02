# detail.py

import reflex as rx 
from ..ui.base import base_page
from . import state
from ..blog.notfound import blog_post_not_found


def article_detail_page() -> rx.Component:
    my_child = rx.cond(
        state.ArticlePublicState.post, 
        rx.vstack(
            # --- SECCIÓN 1: MOSTRAR LA IMAGEN ---
            # Este bloque muestra la imagen si ya tiene una URL.
            # Se actualizará automáticamente después de subir una nueva.
            rx.cond(
                state.ArticlePublicState.post.image_url,
                rx.image(
                    src=state.ArticlePublicState.post.image_url,
                    width="100%",
                    max_width="700px",
                    height="auto",
                    border_radius="15px",
                    margin_y="1em"
                )
            ),
            
            # --- Contenido del artículo (sin cambios) ---
            rx.heading(state.ArticlePublicState.post.title, size="9"),
            rx.text("By ", state.ArticlePublicState.post.userinfo.user.username),
            rx.text(state.ArticlePublicState.post.publish_date),
            rx.text(
                state.ArticlePublicState.post.content,
                white_space='pre-wrap'
            ),
            
            rx.divider(width="100%", margin_y="2em"),

            # --- SECCIÓN 2: SUBIR UNA NUEVA IMAGEN ---
            # Este es el nuevo componente para subir la imagen.
            rx.vstack(
                rx.heading("Subir o Cambiar Imagen", size="4"),
                rx.upload(
                    rx.text(
                        "Arrastra una imagen o haz clic para seleccionar.",
                        font_size="0.9em"
                    ),
                    id="upload_image", # Asignamos un ID para poder resetearlo
                    border="1px dotted rgb(107,114,128)",
                    padding="2em",
                    width="100%"
                ),
                rx.button(
                    "Guardar Imagen",
                    on_click=state.ArticlePublicState.handle_upload(
                        rx.upload_files(upload_id="upload_image")
                    ),
                    width="100%"
                ),
                spacing="4",
                width="100%",
                max_width="500px",
                align="center"
            ),
            
            spacing="5",
            align="center",
            min_height="85vh",
        ),
        blog_post_not_found()
    )
    return base_page(my_child)