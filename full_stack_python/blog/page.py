import reflex as rx
from full_stack_python.blog.state import BlogPublicState
from full_stack_python.navigation import routes


def blog_public_page():
    return rx.center(
        rx.vstack(
            rx.heading("Publicaciones", size="5"),

            rx.grid(
                rx.foreach(
                    BlogPublicState.posts,
                    lambda post: rx.box(
                        rx.link(
                            rx.vstack(
                                # Imagen o fallback
                                rx.cond(
                                    post.images & (post.images.length() > 0),
                                    rx.image(
                                        src=rx.get_upload_url(post.images[0]),
                                        width="100%",
                                        height="200px",
                                        object_fit="cover",
                                        border_radius="md"
                                    ),
                                    rx.box(
                                        "Sin imagen",
                                        width="100%",
                                        height="200px",
                                        bg="gray.100",
                                        color="gray.500",
                                        display="flex",
                                        align_items="center",
                                        justify_content="center",
                                        border_radius="md"
                                    )
                                ),

                                # Título
                                rx.text(
                                    post.title,
                                    font_weight="bold",
                                    color="blue.600"
                                ),

                                # Precio con condicional válido
                                rx.cond(
                                    post.price > 0,
                                    rx.text(f"${{post.price:.2f}}", color="gray.600"),
                                    rx.text("$0.00", color="gray.600")
                                ),

                                spacing="2",
                                align="start",
                                width="100%"
                            ),
                            href=f"{routes.PUBLIC_POST_ROUTE}/{post.id}",
                            style={"textDecoration": "none"}
                        ),
                        border="1px solid #ddd",
                        border_radius="8px",
                        padding="1em",
                        width="100%"
                    )
                ),
                columns="repeat(auto-fit, minmax(220px, 1fr))",
                spacing="4",
                width="100%"
            ),

            spacing="6",
            width="100%",
            max_width="1200px",
            padding="2em",
            on_mount=BlogPublicState.on_load
        )
    )
