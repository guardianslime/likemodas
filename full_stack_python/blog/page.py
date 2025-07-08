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
                                rx.cond(
                                    post.images & (post.images.length() > 0),
                                    rx.image(
                                        src=rx.get_upload_url(post.images[0]),
                                        width="100%",  # Ajustable
                                        max_height="180px",
                                        object_fit="cover",
                                        border_radius="md"
                                    ),
                                    rx.box(
                                        "Sin imagen",
                                        width="100%",
                                        height="150px",
                                        bg="#eee",
                                        align="center",
                                        justify="center"
                                    )
                                ),
                                rx.text(post.title, weight="bold"),
                                rx.text(f"${{post.price}}", color="gray"),  # ✅ Precio como texto
                                spacing="2",
                                align="start"
                            ),
                            href=f"{routes.PUBLIC_POST_ROUTE}/{post.id}"
                        ),
                        padding="1em",
                        border="1px solid #ccc",
                        border_radius="8px",
                        box_shadow="md"
                    )
                ),
                columns="repeat(auto-fit, minmax(220px, 1fr))",
                spacing="4",
                width="100%"
            ),

            spacing="6",
            width="100%",
            padding="2em"
        ),
        width="100%"
    )