import reflex as rx
from full_stack_python.blog.state import BlogViewState


def blog_post_view_page():
    return rx.center(
        rx.vstack(
            # Título
            rx.heading(
                rx.cond(
                    BlogViewState.post,
                    BlogViewState.post.title,
                    "Cargando publicación..."
                ),
                size="3",
                text_align="center"
            ),

            # Imagen + navegación tipo slider
            rx.cond(
                BlogViewState.post & BlogViewState.post.images,
                rx.box(
                    rx.hstack(
                        # Botón izquierdo
                        rx.button(
                            "←",
                            on_click=BlogViewState.anterior_imagen,
                            disabled=BlogViewState.img_idx == 0,
                            size="1",
                        ),
                        # Imagen principal
                        rx.image(
                            src=rx.cond(
                                BlogViewState.imagen_actual != "",
                                rx.get_upload_url(BlogViewState.imagen_actual),
                                ""
                            ),
                            width="100%",
                            max_width="400px",
                            object_fit="contain",
                            border_radius="md",
                            box_shadow="lg"
                        ),
                        # Botón derecho
                        rx.button(
                            "→",
                            on_click=BlogViewState.siguiente_imagen,
                            disabled=BlogViewState.img_idx >= BlogViewState.max_img_idx,
                            size="1",
                        ),
                        justify="center",
                        spacing="3",
                        wrap="wrap",
                    ),
                    width="100%",
                    style={
                        "textAlign": "center",
                        "padding": "1em",
                        "@media (max-width: 500px)": {
                            "flexDirection": "column",
                            "gap": "1em",
                        },
                    }
                ),
                rx.text("No hay imágenes para mostrar.")
            ),

            # Contador de imagen actual
            rx.cond(
                BlogViewState.image_counter != "",
                rx.text(
                    BlogViewState.image_counter,
                    font_size="0.9em",
                    color="gray.500"
                ),
            ),

            # Precio (seguro con formateo)
            rx.cond(
                BlogViewState.formatted_price != "",
                rx.text(
                    BlogViewState.formatted_price,
                    font_weight="bold",
                    color="green.500",
                    font_size="1.2em"
                ),
            ),

            # Contenido (descripción)
            rx.cond(
                BlogViewState.content != "",
                rx.text(
                    BlogViewState.content,
                    padding_top="1em",
                    font_size="1em",
                    text_align="justify"
                ),
            ),

            spacing="6",
            padding="2em",
            align="center",
            width="100%",
            max_width="600px"
        )
    )
