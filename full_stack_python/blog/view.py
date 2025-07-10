import reflex as rx
from ..ui.base import base_layout_component
from full_stack_python.blog.state import BlogViewState

def blog_post_view_page():
    return base_layout_component(
        rx.center(
            rx.cond(
                BlogViewState.post,
                rx.responsive_grid(
                    # Left section (image + nav arrows)
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
                                max_width="500px",
                                max_height="500px",
                                object_fit="cover",
                                border_radius="md",
                                box_shadow="lg"
                            ),
                            position="relative",
                            width="100%",
                            height="100%",
                            aspect_ratio="1 / 1",
                        ),
                        # Flecha izquierda
                        rx.button(
                            "←",
                            on_click=BlogViewState.anterior_imagen,
                            disabled=BlogViewState.img_idx == 0,
                            position="absolute",
                            left="-1.5em",  # fuera de la imagen, mitad de tarjeta
                            top="50%",
                            transform="translateY(-50%)",
                            z_index="1",
                            variant="soft",
                            size="4"
                        ),
                        # Flecha derecha
                        rx.button(
                            "→",
                            on_click=BlogViewState.siguiente_imagen,
                            disabled=BlogViewState.img_idx >= BlogViewState.max_img_idx,
                            position="absolute",
                            right="-1.5em",  # fuera de la imagen, mitad de tarjeta
                            top="50%",
                            transform="translateY(-50%)",
                            z_index="1",
                            variant="soft",
                            size="4"
                        ),
                        position="relative",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        max_width="500px",
                        width="100%",
                        height="auto",
                        padding="1em"
                    ),

                    # Right section (text content)
                    rx.vstack(
                        rx.heading(
                            BlogViewState.post.title,
                            size="8",
                            color=rx.color_mode_cond("black", "white"),
                            width="100%",
                        ),
                        rx.text(
                            BlogViewState.formatted_price,
                            font_size="1.8em",
                            font_weight="bold",
                            color=rx.color_mode_cond("black", "white"),
                            width="100%",
                        ),
                        rx.text(
                            BlogViewState.content,
                            white_space="normal",
                            word_break="break-word",
                            text_align="justify",
                            color=rx.color_mode_cond("black", "white"),
                            width="100%",
                        ),
                        rx.text(
                            BlogViewState.image_counter,
                            font_size="0.9em",
                            color="gray",
                            padding_top="0.5em"
                        ),
                        spacing="5",
                        align="start",
                        width="100%",
                        padding="1em"
                    ),

                    columns=["1fr"] if rx.mobile_only() else ["1fr", "1fr"],
                    spacing="6",
                    width="100%",
                    max_width="1200px",
                    align_items="center",
                    justify_content="center",
                    position="relative"
                ),
                rx.text("Cargando publicación...")
            ),
            width="100%",
            padding="2em"
        )
    )
