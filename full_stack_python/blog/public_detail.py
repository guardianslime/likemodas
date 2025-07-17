import reflex as rx
import reflex_local_auth
from ..navigation.state import NavState
from .state import BlogViewState
from .. import navigation
from ..navigation.device import NavDeviceState
from ..navigation.state import force_reload_go_to
from ..ui.base import fixed_color_mode_button
from ..ui.search_state import SearchState
from ..ui.nav import public_navbar

def standalone_public_layout(child: rx.Component) -> rx.Component:
    return rx.fragment(
        public_navbar(),
        rx.box(
            child,
            padding_y="2em",
            padding_top="6rem",
            width="100%",
            margin="0 auto",
        ),
        fixed_color_mode_button(),
    )

def blog_public_detail_page() -> rx.Component:
    content_grid = rx.cond(
        BlogViewState.has_post,
        rx.grid(
            _image_section(),
            _info_section(),
            columns={"base": "1", "md": "2"},
            spacing="4",
            align_items="start",
            width="100%",
            max_width="1120px",
        ),
        rx.center(rx.text("Publicación no encontrada.", color="red"))
    )

    page_content = rx.center(
        rx.vstack(
            rx.heading("Detalle del Producto", size="8", margin_bottom="1em"),
            content_grid,
            spacing="6",
            width="100%",
            padding="2em",
            align="center",
        ),
        width="100%",
    )

    return standalone_public_layout(page_content)

def _image_section() -> rx.Component:
    image_src = rx.cond(
        BlogViewState.imagen_actual != "",
        rx.get_upload_url(BlogViewState.imagen_actual),
        "/no_image.png"
    )

    return rx.box(
        rx.image(
            src=image_src,
            width="100%",
            height="auto",
            max_height="550px",
            object_fit="contain",
            border_radius="md",
            transition="transform 0.3s ease-in-out",
        ),
        rx.icon(
            tag="arrow_big_left",
            position="absolute",
            left="0.5em",
            top="50%",
            transform="translateY(-50%)",
            on_click=BlogViewState.anterior_imagen,
            cursor="pointer",
            box_size="2em",
            z_index=2,
            color="white",
            bg="rgba(0,0,0,0.3)",
            border_radius="full",
            padding="0.2em",
        ),
        rx.icon(
            tag="arrow_big_right",
            position="absolute",
            right="0.5em",
            top="50%",
            transform="translateY(-50%)",
            on_click=BlogViewState.siguiente_imagen,
            cursor="pointer",
            box_size="2em",
            z_index=2,
            color="white",
            bg="rgba(0,0,0,0.3)",
            border_radius="full",
            padding="0.2em",
        ),
        width="100%",
        max_width="600px",
        position="relative",
        border_radius="md",
        overflow="hidden",

        # 🎯 GESTOS TÁCTILES
        on_touch_start=BlogViewState.on_touch_start,
        on_touch_end=BlogViewState.on_touch_end,

        # 🖱️ TAMBIÉN CON MOUSE (opcional para escritorio)
        on_mouse_down=BlogViewState.on_touch_start,
        on_mouse_up=BlogViewState.on_touch_end,
    )

def _info_section() -> rx.Component:
    return rx.vstack(
        rx.text(
            BlogViewState.post.title,
            size="7",
            font_weight="bold",
            margin_bottom="0.5em",
            text_align="left",
        ),
        rx.text(
            BlogViewState.formatted_price,
            size="6",
            color="gray",
            text_align="left",
        ),
        rx.text(
            BlogViewState.content,
            size="4",
            margin_top="1em",
            white_space="pre-wrap",
            text_align="left",
        ),
        padding="1em",
        align="start",
        width="100%",
    )
