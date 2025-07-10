import reflex as rx
from full_stack_python.public_post.state import BlogViewState
from full_stack_python.ui.base import base_layout_component

def public_post_detail_page():
    # Vista común que se adapta a tamaños
    def content():
        return rx.hstack(
            # Imagen + flechas
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
                rx.icon(
                    tag="arrow_big_left",
                    position="absolute",
                    left="0.5em",
                    top="50%",
                    transform="translateY(-50%)",
                    on_click=BlogViewState.anterior_imagen,
                    cursor="pointer",
                    box_size="2em"
                ),
                rx.icon(
                    tag="arrow_big_right",
                    position="absolute",
                    right="0.5em",
                    top="50%",
                    transform="translateY(-50%)",
                    on_click=BlogViewState.siguiente_imagen,
                    cursor="pointer",
                    box_size="2em"
                ),
                width="100%",
                max_width="600px",
                height="400px",
                position="relative",
                border_radius="md",
                overflow="hidden",
            ),
            # Info
            rx.box(
                rx.vstack(
                    rx.text(
                        BlogViewState.post.title,
                        size="6",
                        font_weight="bold",
                        margin_bottom="0.5em"
                    ),
                    rx.text(
                        BlogViewState.formatted_price,
                        size="5",
                        color="gray"
                    ),
                    rx.text(
                        BlogViewState.content,
                        size="4",
                        margin_top="1em",
                        white_space="pre-wrap"
                    )
                ),
                width="100%",
                padding="1em"
            ),
            spacing="6",
            width="100%",
            align_items="start",
            wrap="wrap"
        )

    return base_layout_component(
        rx.box(
            rx.cond(
                BlogViewState.has_post,
                rx.fragment(
                    rx.mobile_only(content()),
                    rx.tablet_only(content()),
                    rx.desktop_only(content()),
                ),
                rx.center(
                    rx.text("Publicación no encontrada.", color="red")
                )
            ),
            padding="2em",
            width="100%",
            max_width="1440px",
            margin="0 auto"
        ),
        on_mount=BlogViewState.on_load
    )
