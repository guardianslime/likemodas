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
                                # Contenedor de imagen centrado
                                rx.box(
                                    rx.cond(
                                        post.images & (post.images.length() > 0),
                                        rx.image(
                                            src=rx.get_upload_url(post.images[0]),
                                            width="100%",
                                            height="200px",  # Altura fija
                                            object_fit="cover",
                                            border_radius="md"
                                        ),
                                        rx.box(
                                            "Sin imagen",
                                            width="100%",
                                            height="200px",
                                            bg="#eee",
                                            align="center",
                                            justify="center",
                                            display="flex",
                                            border_radius="md"
                                        )
                                    ),
                                    height="200px",  # Altura fija del contenedor
                                    width="100%",
                                    display="flex",
                                    justify_content="center",
                                    align_items="center"
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
                                align="start"
                            ),
                            href=f"{routes.PUBLIC_POST_ROUTE}/{post.id}"
                        ),
                        padding="1em",
                        border="1px solid #ccc",
                        border_radius="8px",
                        box_shadow="md",
                        min_height="280px"  # Altura total fija para que no brinque
                    )
                ),
                columns="repeat(auto-fit, minmax(200px, 1fr))",  # un poco más grande
                max_width="1200px",  # espacio para hasta 6 columnas en pantallas grandes
                spacing="4",
                width="100%"
            ),

            spacing="6",
            width="100%",
            padding="2em"
        ),
        width="100%"
    )
