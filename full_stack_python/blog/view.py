import reflex as rx
from full_stack_python.blog.state import BlogViewState
from full_stack_python.navigation import routes

def blog_post_view_page():
    return rx.box(
        rx.vstack(
            rx.heading(
                rx.cond(
                    BlogViewState.has_post,
                    BlogViewState.post.title,
                    "Cargando..."
                ),
                size="6",
                padding_bottom="1em"
            ),

            rx.hstack(
                # Imagen con flechas de navegación
                rx.box(
                    rx.box(
                        rx.image(
                            src=rx.cond(
                                BlogViewState.imagen_actual != "",
                                rx.get_upload_url(BlogViewState.imagen_actual),
                                "/no_image.png"
                            ),
                            width="100%",
                            height="100%",
                            object_fit="contain",
                            border_radius="md"
                        ),
                        width="100%",
                        height="100%",
                        position="relative"
                    ),

                    # Botón Izquierda
                    rx.button(
                        "◀",
                        position="absolute",
                        left="0.5em",
                        top="50%",
                        transform="translateY(-50%)",
                        on_click=BlogViewState.imagen_anterior,
                        variant="ghost"
                    ),

                    # Botón Derecha
                    rx.button(
                        "▶",
                        position="absolute",
                        right="0.5em",
                        top="50%",
                        transform="translateY(-50%)",
                        on_click=BlogViewState.imagen_siguiente,
                        variant="ghost"
                    ),

                    width="60%",
                    max_width="600px",
                    height="500px",
                    position="relative",
                    border_radius="md",
                    overflow="hidden",
                ),

                # Info del producto
                rx.box(
                    rx.vstack(
                        rx.text(
                            BlogViewState.post.title,
                            size="6",
                            font_weight="bold",
                            margin_bottom="0.5em",
                            white_space="pre-wrap"
                        ),
                        rx.text(
                            BlogViewState.formatted_price,
                            size="5",
                            color="gray",
                            white_space="pre-wrap"
                        ),
                        rx.text(
                            BlogViewState.content,
                            size="4",
                            margin_top="1em",
                            white_space="pre-wrap"
                        )
                    ),
                    width="40%",
                    padding="2em"
                ),

                spacing="6",
                width="100%",
                align_items="start",
                wrap="wrap"
            )
        ),
        padding="2em",
        width="100%",
        max_width="1440px",
        margin="0 auto"
    )
