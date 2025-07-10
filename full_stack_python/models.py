import reflex as rx
from ..ui.base import base_layout_component
from full_stack_python.blog.state import BlogViewState

def blog_post_view_page():
    return base_layout_component(
        rx.center(
            rx.box(
                rx.cond(
                    BlogViewState.post,
                    rx.flex(
                        # Imagen y navegación
                        rx.box(
                            rx.hstack(
                                rx.button(
                                    "←",
                                    on_click=BlogViewState.anterior_imagen,
                                    disabled=BlogViewState.img_idx == 0,
                                    size="3",
                                ),
                                rx.box(
                                    rx.image(
                                        src=rx.cond(
                                            BlogViewState.imagen_actual != "",
                                            rx.get_upload_url(BlogViewState.imagen_actual),
                                            ""
                                        ),
                                        width="350px",
                                        height="350px",
                                        object_fit="cover",
                                        border_radius="md",
                                        box_shadow="lg"
                                    ),
                                    position="relative",
                                ),
                                rx.button(
                                    "→",
                                    on_click=BlogViewState.siguiente_imagen,
                                    disabled=BlogViewState.img_idx >= BlogViewState.max_img_idx,
                                    size="3",
                                ),
                                align="center",
                                spacing="3",
                            ),
                            flex_shrink="0"
                        ),
                        # Información a la derecha
                        rx.vstack(
                            rx.heading(BlogViewState.post.title, size="7"),
                            rx.text(BlogViewState.formatted_price, color="green.500", weight="bold", size="6"),
                            rx.text(BlogViewState.content, white_space="pre-wrap", size="5"),
                            rx.text(BlogViewState.image_counter, size="4", color="gray.500"),
                            spacing="4",
                            align="start",
                            width="100%",
                        ),
                        spacing="8",
                        align="center",
                        wrap="wrap",
                        width="100%",
                        max_width="1000px",
                    ),
                    rx.text("No se encontró la publicación.")
                ),
                padding="2em",
                width="100%",
            )
        )
    )
