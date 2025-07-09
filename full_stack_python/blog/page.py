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
                                # Imagen centrada en contenedor fijo
                                rx.box(
                                    rx.cond(
                                        post.images & (post.images.length() > 0),
                                        rx.image(
                                            src=rx.get_upload_url(post.images[0]),
                                            width="auto",
                                            height="100%",
                                            max_height="180px",
                                            object_fit="cover",
                                            border_radius="md"
                                        ),
                                        rx.box(
                                            "Sin imagen",
                                            color="gray",
                                            font_size="sm",
                                            display="flex",
                                            align_items="center",
                                            justify_content="center",
                                            width="100%",
                                            height="180px",
                                            bg="#f5f5f5",
                                            border_radius="md"
                                        )
                                    ),
                                    display="flex",
                                    align_items="center",
                                    justify_content="center",
                                    height="180px",
                                    width="100%",
                                    overflow="hidden",
                                    border_radius="md",
                                    bg="white"
                                ),
                                # Título
                                rx.text(post.title, weight="bold"),
                                # Precio
                                rx.text(
                                    rx.cond(
                                        post.price,
                                        "$" + post.price.to(str),
                                        "$0.00"
                                    ),
                                    color="gray"
                                ),
                                spacing="2",
                                align="start",
                                width="100%"
                            ),
                            href=f"{routes.PUBLIC_POST_ROUTE}/{post.id}"
                        ),
                        padding="1em",
                        border="1px solid #ccc",
                        border_radius="8px",
                        box_shadow="md",
                        min_height="280px",
                        bg="white"
                    )
                ),
                columns="repeat(auto-fit, minmax(200px, 1fr))",
                max_width="1200px",
                spacing="4",
                width="100%"
            ),

            spacing="6",
            width="100%",
            padding="2em"
        ),
        width="100%"
    )
