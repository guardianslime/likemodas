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
                            size="2",  # ← cambiado de "sm"
                        ),
                        # Imagen principal
                        rx.image(
                            src=rx.cond(
                                BlogViewState.post,
                                rx.get_upload_url(BlogViewState.post.images[BlogViewState.img_idx]),
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
                            disabled=rx.cond(
                                BlogViewState.post,
                                BlogViewState.img_idx == BlogViewState.max_img_idx,
                                True
                            ),
                            size="2",  # ← cambiado de "sm"
                        ),
                        justify="center",
                        spacing="4",
                        wrap="wrap",
                    ),
                    width="100%",
                    style={
                        "textAlign": "center",
                        "padding": "4",
                        "@media (max-width: 500px)": {
                            "flexDirection": "column",
                            "gap": "4",
                        },
                    }
                ),
                rx.text("No hay imágenes para mostrar.")
            ),

            # Contador de imagen actual
            rx.text(
                f"{BlogViewState.img_idx + 1} / "
                f"{rx.cond(BlogViewState.post, BlogViewState.post.images.length(), 1)}",
                font_size="4",
                color="gray.500"
            ),

            # Precio
            rx.text(
                rx.cond(
                    BlogViewState.post,
                    f"${{BlogViewState.post.price:.2f}}",
                    ""
                ),
                font_weight="bold",
                color="green.500",
                font_size="4.2"
            ),

            # Contenido
            rx.text(
                rx.cond(
                    BlogViewState.post,
                    BlogViewState.post.content,
                    ""
                ),
                padding_top="4",
                font_size="4",
                text_align="justify"
            ),

            spacing="4",
            padding="8",
            align="center",
            width="100%",
            max_width="600px"
        )
    )
