import reflex as rx
from ..ui.base import base_layout_component
from full_stack_python.blog.state import BlogPublicState
from full_stack_python.navigation import routes

def blog_public_page():
    return base_layout_component(
        rx.center(
            rx.vstack(
                rx.heading("Publicaciones", size="5"),

                rx.fragment(

                    # Vista solo en móvil: 2 columnas
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
                                                        height="270px",
                                                        object_fit="cover",
                                                        border_radius="md"
                                                    ),
                                                    rx.box(
                                                        "Sin imagen",
                                                        width="100%",
                                                        height="270px",
                                                        bg="#eee",
                                                        align="center",
                                                        justify="center",
                                                        display="flex",
                                                        border_radius="md"
                                                    )
                                                ),
                                                height="270px",
                                                width="100%",
                                                display="flex",
                                                justify_content="center",
                                                align_items="center"
                                            ),
                                            rx.text(post.title, weight="bold"),
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
                                    min_height="400px"
                                )
                            ),
                            columns="repeat(2, 1fr)",
                            spacing="4",
                            width="100%",
                            justify_content="center"
                        )
                    ),

                    # Vista solo en tablet: 3 columnas
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
                                                        height="270px",
                                                        object_fit="cover",
                                                        border_radius="md"
                                                    ),
                                                    rx.box(
                                                        "Sin imagen",
                                                        width="100%",
                                                        height="270px",
                                                        bg="#eee",
                                                        align="center",
                                                        justify="center",
                                                        display="flex",
                                                        border_radius="md"
                                                    )
                                                ),
                                                height="270px",
                                                width="100%",
                                                display="flex",
                                                justify_content="center",
                                                align_items="center"
                                            ),
                                            rx.text(post.title, weight="bold"),
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
                                    min_height="400px"
                                )
                            ),
                            columns="repeat(3, 1fr)",
                            spacing="4",
                            width="100%",
                            justify_content="center"
                        )
                    ),

                    # Vista solo en desktop: 6 columnas, con zoom al hover
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
                                                        height="270px",
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
                                                        height="270px",
                                                        bg="#eee",
                                                        align="center",
                                                        justify="center",
                                                        display="flex",
                                                        border_radius="md"
                                                    )
                                                ),
                                                height="270px",
                                                width="100%",
                                                display="flex",
                                                justify_content="center",
                                                align_items="center"
                                            ),
                                            rx.text(post.title, weight="bold"),
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
                                    min_height="400px"
                                )
                            ),
                            columns="repeat(6, 1fr)",
                            spacing="4",
                            width="100%",
                            max_width="1200px",
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
