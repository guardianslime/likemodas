import reflex as rx
from full_stack_python.blog.state import BlogViewState

def blog_post_view_page():
    return rx.center(
        rx.hstack(
            # Imagen con flechas a los lados
            rx.box(
                rx.hstack(
                    rx.button(
                        "←",
                        on_click=BlogViewState.anterior_imagen,
                        disabled=BlogViewState.img_idx == 0,
                        size="3"
                    ),
                    rx.box(
                        rx.cond(
                            BlogViewState.imagen_actual != "",
                            rx.image(
                                src=rx.get_upload_url(BlogViewState.imagen_actual),
                                width="350px",
                                height="350px",
                                object_fit="cover",
                                border_radius="md",
                                box_shadow="lg"
                            ),
                            rx.box(
                                "Sin imagen",
                                width="350px",
                                height="350px",
                                bg="#eee",
                                align="center",
                                justify="center",
                                display="flex",
                                border_radius="md"
                            )
                        ),
                        position="relative"
                    ),
                    rx.button(
                        "→",
                        on_click=BlogViewState.siguiente_imagen,
                        disabled=BlogViewState.img_idx >= BlogViewState.max_img_idx,
                        size="3"
                    ),
                    spacing="3",
                    align="center",
                    justify="center"
                ),
                width="100%",
                max_width="600px"
            ),

            # Información a la derecha
            rx.box(
                rx.vstack(
                    rx.heading(
                        BlogViewState.post.title if BlogViewState.post else "Cargando...",
                        size="6",
                        text_align="start"
                    ),
                    rx.text(
                        BlogViewState.formatted_price,
                        font_weight="bold",
                        color="green.500",
                        size="5"
                    ),
                    rx.text(
                        BlogViewState.content,
                        white_space="pre-wrap",
                        max_width="400px",
                        text_align="start"
                    ),
                    spacing="4",
                    align="start"
                ),
                padding="2em",
                max_width="500px"
            ),

            spacing="8",
            wrap="wrap",
            justify="center",
            align="start",
            width="100%"
        ),
        width="100%",
        padding="3em"
    )
