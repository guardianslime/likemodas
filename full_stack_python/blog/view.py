import reflex as rx
from full_stack_python.blog.state import BlogViewState
from full_stack_python.navigation import routes


def blog_post_view_page():
    return rx.box(
        rx.vstack(
            # Título eliminado de la parte superior como solicitaste

            rx.hstack(
                # Sección de imagen + flechas centradas en el contenedor
                rx.box(
                    rx.box(
                        rx.image(
                            src=rx.cond(
                                BlogViewState.imagen_actual != "",
                                rx.get_upload_url(BlogViewState.imagen_actual),
                                "/no_image.png",
                            ),
                            width="100%",
                            height="100%",
                            object_fit="contain",
                            border_radius="md",
                        ),
                        width="100%",
                        height="100%",
                        position="relative",
                    ),
                    # Flechas centradas en la mitad del contenedor
                    rx.icon(
                        tag="arrow-big-left",
                        position="absolute",
                        left="1em",
                        top="50%",
                        transform="translateY(-50%)",
                        size=32,
                        on_click=BlogViewState.anterior_imagen,
                        cursor="pointer",
                        color="white",
                    ),
                    rx.icon(
                        tag="arrow-big-right",
                        position="absolute",
                        right="1em",
                        top="50%",
                        transform="translateY(-50%)",
                        size=32,
                        on_click=BlogViewState.siguiente_imagen,
                        cursor="pointer",
                        color="white",
                    ),
                    width="60%",
                    max_width="600px",
                    height="500px",
                    position="relative",
                    border_radius="md",
                    overflow="hidden",
                ),

                # Sección de información del post
                rx.box(
                    rx.vstack(
                        rx.text(
                            rx.cond(
                                BlogViewState.post & BlogViewState.post.title,
                                BlogViewState.post.title,
                                "Cargando..."
                            ),
                            size="6",
                            font_weight="bold",
                            color=rx.cond(
                                rx.color_mode() == "dark",
                                "white",
                                "black"
                            ),
                            margin_bottom="0.5em",
                            width="100%",
                            word_break="break-word"
                        ),
                        rx.text(
                            BlogViewState.formatted_price,
                            size="5",
                            color=rx.cond(
                                rx.color_mode() == "dark",
                                "gray.400",
                                "gray.700"
                            ),
                            width="100%",
                            word_break="break-word"
                        ),
                        rx.text(
                            BlogViewState.content,
                            size="4",
                            white_space="pre-wrap",
                            color=rx.cond(
                                rx.color_mode() == "dark",
                                "gray.200",
                                "gray.800"
                            ),
                            margin_top="1em",
                            width="100%",
                            word_break="break-word"
                        )
                    ),
                    width="40%",
                    padding="2em",
                ),
                spacing="6",
                width="100%",
                align_items="start",
                wrap="wrap",
            ),
        ),
        padding="2em",
        width="100%",
        max_width="1440px",
        margin="0 auto",
        on_mount=BlogViewState.on_load  # ← importante para cargar el post al entrar
    )
