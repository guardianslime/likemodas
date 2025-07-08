import reflex as rx
from full_stack_python.blog.state import BlogPublicState


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
                                    (post.images != None) & (post.images.length() > 0),
                                    rx.image(src=rx.get_upload_url(post.images[0]), width="200px"),
                                    rx.box("Sin imagen", width="200px", height="150px", bg="#eee", align="center", justify="center")
                                ),
                                rx.text(post.title, weight="bold"),
                                rx.text(
                                    rx.cond(
                                        post.price != 0,
                                        f"${{post.price:.2f}}",  # Doble llave para escapar dentro del string
                                        "$0.00"
                                    ),
                                    color="gray"
                                )
                                spacing="2",
                                align="start"
                            ),
                            href=f"/public-post/{post.id}"
                        ),
                        padding="1em",
                        border="1px solid #ccc",
                        border_radius="8px",
                    )
                ),
                columns="repeat(auto-fit, minmax(220px, 1fr))",
                spacing="4",
                width="100%"
            ),

            spacing="6",
            width="100%",
            max_width="1000px",
            padding="2em"
        )
    )
