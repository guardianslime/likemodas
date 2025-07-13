import reflex as rx
from full_stack_python.ui.base import base_layout_component
from full_stack_python.public_post.state import BlogViewState, BlogListState, BlogCard


def public_post_detail_page() -> rx.Component:
    return base_layout_component(
        rx.box(
            rx.cond(
                BlogViewState.has_post,
                _responsive_layout(),
                rx.center(rx.text("Publicación no encontrada.", color="red"))
            ),
            padding="2em",
            width="100%",
            max_width="1440px",
            margin="0 auto",
        ),
        on_mount=BlogViewState.on_load
    )


def blog_post_list_page() -> rx.Component:
    return base_layout_component(
        rx.box(
            rx.cond(
                BlogListState.blog_posts != [],
                rx.grid(
                    *[BlogCard(post=p) for p in BlogListState.blog_posts],
                    columns=["1fr", "1fr", "repeat(6, 1fr)"],
                    spacing="4",
                    width="100%",
                ),
                rx.center(rx.text("No hay publicaciones disponibles.", color="red"))
            ),
            width="100%",
            padding="2em",
            max_width="1440px",
            margin="0 auto",
        ),
        on_mount=BlogListState.load_posts
    )


def _responsive_layout() -> rx.Component:
    return rx.grid(
        _image_section(),
        _info_section(),
        columns=rx.breakpoints(sm="1fr", lg="1fr 1fr"),  # Móvil: una columna. Escritorio: dos.
        spacing="2em",
        align_items="start",
        width="100%",
        max_width="1440px",
    )


def _image_section(width: str = "100%", height: str = "550px") -> rx.Component:
    return rx.box(
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
        width=width,
        max_width="600px",  # Fijo como en escritorio
        height=height,
        position="relative",
        border_radius="md",
        overflow="hidden"
    )


def _info_section() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text(
                BlogViewState.post.title,
                size="6",
                font_weight="bold",
                margin_bottom="0.5em",
                text_align=rx.breakpoints(sm="left", lg="left")
            ),
            rx.text(
                BlogViewState.formatted_price,
                size="5",
                color="gray",
                text_align=rx.breakpoints(sm="left", lg="left")
            ),
            rx.text(
                BlogViewState.content,
                size="4",
                margin_top="1em",
                white_space="pre-wrap",
                text_align=rx.breakpoints(sm="left", lg="left")
            )
        ),
        padding="2em",
        align="start"
    )
