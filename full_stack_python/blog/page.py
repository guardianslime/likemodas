import reflex as rx
from ..ui.base import base_layout_component
from full_stack_python.blog.state import BlogPublicState
from full_stack_python.navigation import routes

def blog_public_page():
    return base_layout_component(
        rx.center(
            rx.vstack(
                rx.heading("Publicaciones", size="6"),
                rx.fragment(

                    # Mobile
                    rx.mobile_only(
                        rx.grid(
                            rx.foreach(
                                BlogPublicState.posts,
                                lambda post: rx.box(
                                    rx.link(
                                        rx.vstack(
                                            rx.box(
                                                rx.cond(
                                                    post.images & (post.images.length() > 0),
                                                    rx.image(
                                                        src=rx.get_upload_url(post.images[0]),
                                                        width="100%",
                                                        height="100%",
                                                        object_fit="cover",
                                                        border_radius="md"
                                                    ),
                                                    rx.box(
                                                        "Sin imagen",
                                                        width="100%",
                                                        height="100%",
                                                        bg="#eee",
                                                        align="center",
                                                        justify="center",
                                                        display="flex",
                                                        border_radius="md"
                                                    )
                                                ),
                                                position="relative",
                                                width="350px",
                                                height="350px"
                                            ),
                                            rx.text(post.title, weight="bold", size="6"),
                                            rx.text(
                                                rx.cond(
                                                    post.price,
                                                    "$" + post.price.to(str),
                                                    "$0.00"
                                                ),
                                                color="gray",
                                                size="6"
                                            ),
                                            spacing="2",
                                            align="start"
                                        ),
                                        href=f"{routes.PUBLIC_POST_ROUTE}/{post.id}"
                                    ),
                                    padding="7em",
                                    border="1px solid #ccc",
                                    border_radius="8px",
                                    box_shadow="md"
                                )
                            ),
                            columns="repeat(2, 1fr)",
                            spacing="6",
                            width="100%",
                            justify_content="center"
                        )
                    ),

                    # Tablet
                    rx.tablet_only(
                        rx.grid(
                            rx.foreach(
                                BlogPublicState.posts,
                                lambda post: rx.box(
                                    rx.link(
                                        rx.vstack(
                                            rx.box(
                                                rx.cond(
                                                    post.images & (post.images.length() > 0),
                                                    rx.image(
                                                        src=rx.get_upload_url(post.images[0]),
                                                        width="100%",
                                                        height="100%",
                                                        object_fit="cover",
                                                        border_radius="md"
                                                    ),
                                                    rx.box(
                                                        "Sin imagen",
                                                        width="100%",
                                                        height="100%",
                                                        bg="#eee",
                                                        align="center",
                                                        justify="center",
                                                        display="flex",
                                                        border_radius="md"
                                                    )
                                                ),
                                                position="relative",
                                                width="350px",
                                                height="350px"
                                            ),
                                            rx.text(post.title, weight="bold", size="6"),
                                            rx.text(
                                                rx.cond(
                                                    post.price,
                                                    "$" + post.price.to(str),
                                                    "$0.00"
                                                ),
                                                color="gray",
                                                size="6"
                                            ),
                                            spacing="2",
                                            align="start"
                                        ),
                                        href=f"{routes.PUBLIC_POST_ROUTE}/{post.id}"
                                    ),
                                    padding="7em",
                                    border="1px solid #ccc",
                                    border_radius="8px",
                                    box_shadow="md"
                                )
                            ),
                            columns="repeat(3, 1fr)",
                            spacing="6",
                            width="100%",
                            justify_content="center"
                        )
                    ),

                    # Desktop
                    rx.desktop_only(
                        rx.grid(
                            rx.foreach(
                                BlogPublicState.posts,
                                lambda post: rx.box(
                                    rx.link(
                                        rx.vstack(
                                            rx.box(
                                                rx.cond(
                                                    post.images & (post.images.length() > 0),
                                                    rx.image(
                                                        src=rx.get_upload_url(post.images[0]),
                                                        width="100%",
                                                        height="100%",
                                                        object_fit="cover",
                                                        border_radius="md",
                                                        style={
                                                            "transition": "transform 0.3s ease-in-out",
                                                            "_hover": {
                                                                "transform": "scale(1.05)"
                                                            }
                                                        }
                                                    ),
                                                    rx.box(
                                                        "Sin imagen",
                                                        width="100%",
                                                        height="100%",
                                                        bg="#eee",
                                                        align="center",
                                                        justify="center",
                                                        display="flex",
                                                        border_radius="md"
                                                    )
                                                ),
                                                position="relative",
                                                width="350px",
                                                height="350px"
                                            ),
                                            rx.text(post.title, weight="bold", size="6"),
                                            rx.text(
                                                rx.cond(
                                                    post.price,
                                                    "$" + post.price.to(str),
                                                    "$0.00"
                                                ),
                                                color="gray",
                                                size="6"
                                            ),
                                            spacing="2",
                                            align="start"
                                        ),
                                        href=f"{routes.PUBLIC_POST_ROUTE}/{post.id}"
                                    ),
                                    padding="7em",
                                    border="1px solid #ccc",
                                    border_radius="8px",
                                    box_shadow="md"
                                )
                            ),
                            columns="repeat(6, 1fr)",
                            spacing="6",
                            width="100%",
                            max_width="11200px",
                            justify_content="center"
                        )
                    )
                ),
                spacing="6",
                width="100%",
                padding="2em",
                align="center"
            ),
            width="100%"
        )
    )
