import reflex as rx
from full_stack_python.blog.state import BlogViewState
from full_stack_python.navigation import routes

def blog_post_view_page():
    return rx.box(
        rx.vstack(
            rx.heading(
                rx.cond(
                    BlogViewState.post.is_defined(),
                    BlogViewState.post.title,
                    "Cargando..."
                ),
                size="6",
                padding_bottom="1em"
            ),
            rx.hstack(
                # Sección de la imagen + flechas
                rx.box(
                    rx.box(
                        rx.image(
                            src=rx.cond(
                                BlogViewState.post.images.length() > 0,
                                rx.get_upload_url(BlogViewState.post.images[BlogViewState.imagen_actual]),
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
                    rx.button(
                        "◀",
                        position="absolute",
                        left="0.5em",
                        top="50%",
                        transform="translateY(-50%)",
                        on_click=BlogViewState.imagen_anterior,
                        variant="ghost"
                    ),
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

                # Sección de información del post
                rx.box(
                    rx.vstack(
                        rx.text(
                            BlogViewState.post.title,
                            size="6",
                            font_weight="bold",
                            margin_bottom="0.5em"
                        ),
                        rx.text(
                            rx.cond(
                                BlogViewState.post.price,
                                "$" + BlogViewState.post.price.to(str),
                                "$0.00"
                            ),
                            size="5",
                            color="gray"
                        ),
                        rx.text(
                            BlogViewState.post.description,
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
