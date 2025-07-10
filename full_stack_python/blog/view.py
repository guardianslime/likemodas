import reflex as rx
from ..ui.base import base_layout_component
from full_stack_python.blog.state import BlogViewState


def blog_post_view_page():
    return base_layout_component(
        rx.center(
            rx.cond(
                BlogViewState.post,
                rx.hstack(
                    # Imagen + flechas
                    rx.box(
                        rx.box(
                            rx.image(
                                src=rx.cond(
                                    BlogViewState.imagen_actual != "",
                                    rx.get_upload_url(BlogViewState.imagen_actual),
                                    ""
                                ),
                                width="100%",
                                height="100%",
                                object_fit="cover",
                                border_radius="md",
                                style={
                                    "transition": "transform 0.3s ease-in-out",
                                    "_hover": {
                                        "transform": "scale(1.03)"
                                    }
                                }
                            ),
                            width="100%",
                            padding_top="100%",
                            position="relative",
                            border_radius="md",
                            overflow="hidden"
                        ),
                        # Flecha izquierda
                        rx.button(
                            "←",
                            on_click=BlogViewState.imagen_anterior,
                            position="absolute",
                            left="0.5em",
                            top="50%",
                            transform="translateY(-50%)",
                            z_index="2",
                            variant="ghost"
                        ),
                        # Flecha derecha
                        rx.button(
                            "→",
                            on_click=BlogViewState.imagen_siguiente,
                            position="absolute",
                            right="0.5em",
                            top="50%",
                            transform="translateY(-50%)",
                            z_index="2",
                            variant="ghost"
                        ),
                        width="400px",
                        max_width="100%",
                        position="relative"
                    ),

                    # Texto a la derecha
                    rx.vstack(
                        rx.heading(BlogViewState.post.title, size="6"),
                        rx.text(BlogViewState.formatted_price, weight="bold", color="green", size="5"),
                        rx.text(BlogViewState.content, white_space="pre-wrap"),
                        spacing="4",
                        align="start"
                    ),

                    spacing="8",
                    width="100%",
                    max_width="1200px",
                    align="start",
                    justify="center",
                    wrap="wrap"  # para evitar desbordes en pantallas pequeñas
                ),
                rx.text("Cargando publicación...")
            ),
            width="100%",
            padding="2em"
        )
    )
