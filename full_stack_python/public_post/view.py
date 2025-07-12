import reflex as rx
from full_stack_python.ui.base import base_layout_component
from full_stack_python.blog.state import BlogListState  # Ajusta el import si es diferente
from full_stack_python.navigation.device import DeviceState
from full_stack_python.blog.components import BlogCard  # Asegúrate que este exista
from full_stack_python.blog.state import BlogViewState

def blog_post_list_page() -> rx.Component:
    return base_layout_component(
        rx.box(
            rx.cond(
                DeviceState.is_desktop,
                # 💻 Escritorio: grid de 3 columnas mínimo
                rx.grid(
                    *[BlogCard(post=p) for p in BlogListState.blog_posts],
                    columns=[6],
                    spacing="4",
                    width="100%",
                ),
                # 📱 Móvil / tablet: 2 columnas o 1
                rx.grid(
                    *[BlogCard(post=p) for p in BlogListState.blog_posts],
                    columns=[1, 2],
                    spacing="4",
                    width="100%",
                )
            ),
            width="100%",
            padding="2em",
            max_width="1440px",
            margin="0 auto"
        ),
        on_mount=lambda: [BlogListState.load_posts(), DeviceState.on_mount()]
    )


def layout_escritorio() -> rx.Component:
    return rx.grid(
        _image_section(width="100%", height="550px"),
        _info_section(width="100%"),
        template_columns="3fr 2fr",
        gap="2em",
        width="100%",
        max_width="1440px",
        align_items="start"
    )


def layout_movil() -> rx.Component:
    return rx.vstack(
        _image_section(width="100%", height="350px"),
        _info_section(width="100%"),
        spacing="4",
        width="100%"
    )


def _image_section(width: str = "100%", height: str = "400px") -> rx.Component:
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
        max_width="600px",
        height=height,
        position="relative",
        border_radius="md",
        overflow="hidden"
    )


def _info_section(width: str = "100%") -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text(
                BlogViewState.post.title,
                size="6",
                font_weight="bold",
                margin_bottom="0.5em"
            ),
            rx.text(
                BlogViewState.formatted_price,
                size="5",
                color="gray"
            ),
            rx.text(
                BlogViewState.content,
                size="4",
                margin_top="1em",
                white_space="pre-wrap"
            )
        ),
        width=width,
        padding="2em"
    )
