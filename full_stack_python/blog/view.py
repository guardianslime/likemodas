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
                            size="1",  # ← Cambiado de 'sm' a '1' válido
                        ),
                        # Imagen principal
                        rx.image(
                            src=rx.cond(
                                BlogViewState.post,
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
                        spacing="3",  # ← Corregido: no usar '1em'
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
                BlogViewState.post,
                rx.text(
                    rx.format(
                        "{} / {}",
                        BlogViewState.img_idx + 1,
                        rx.var(BlogViewState.post.images).length()
                    ),
                    font_size="0.9em",
                    color="gray.500"
                ),
                rx.text("")
            ),

            # Precio (mueve hacia abajo correctamente)
            rx.cond(
                BlogViewState.post,
                rx.text(
                    rx.format("${:.2f}", BlogViewState.post.price),
                    font_weight="bold",
                    color="green.500",
                    font_size="1.2em"
                ),
                rx.text("")
            ),

            # Contenido (descripción)
            rx.cond(
                BlogViewState.post,
                rx.text(
                    BlogViewState.post.content,
                    padding_top="1em",
                    font_size="1em",
                    text_align="justify"
                ),
                rx.text("")
            ),

            spacing="6",
            padding="2em",
            align="center",
            width="100%",
            max_width="600px"
        )
    )
