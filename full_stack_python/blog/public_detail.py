# full_stack_python/blog/public_detail.py (CORREGIDO)

import reflex as rx
from .state import BlogViewState 
from ..ui.search_state import SearchState

def _public_detail_header() -> rx.Component:
    """
    Un encabezado simple y estable exclusivo para la página de detalle pública.
    Contiene únicamente una barra de búsqueda para evitar conflictos de layout.
    """
    return rx.box(
        rx.input(
            placeholder="Buscar productos...",
            value=SearchState.search_term,
            on_change=SearchState.update_search,
            on_blur=SearchState.search_action,
            width="100%",
            max_width="760px",
            padding_y="0.75em",
            padding_x="1em",
            border_radius="full",
            border_width="1px",
            border_color="#ccc",
            background_color="white",
            color="black",
        ),
        # Estilos para centrar la barra de búsqueda
        style={
            "display": "flex",
            "justify_content": "center",
            "align_items": "center",
            "width": "100%",
            "padding": "1em",
        }
    )

def blog_public_detail_page() -> rx.Component:
    """
    Página que muestra el detalle de una publicación pública,
    con un layout y encabezado personalizados para evitar conflictos de estilo.
    """
    # ✨ CORRECCIÓN AQUÍ: Se elimina 'on_load' del componente rx.box.
    my_child = rx.box(
        rx.cond(
            BlogViewState.has_post,
            rx.grid(
                _image_section(),
                _info_section(),
                columns={"base": "1", "md": "2"},
                spacing="4",
                align_items="start",
                width="100%",
            ),
            rx.center(rx.text("Publicación no encontrada.", color="red"))
        ),
        padding_y="2em",
        width="100%",
        max_width="1440px",
        margin="0 auto",
    )

    # El evento on_load se gestiona en app.add_page, por lo que se quita de aquí.
    return rx.fragment(
        _public_detail_header(),
        my_child,
        rx.color_mode.button(position="bottom-left"),
    )

def _image_section() -> rx.Component:
    """Sección que muestra la imagen principal y las flechas de navegación."""
    return rx.box(
        rx.image(
            src=rx.cond(
                BlogViewState.imagen_actual != "",
                rx.get_upload_url(BlogViewState.imagen_actual),
                "/no_image.png"
            ),
            width="100%",
            height="auto",
            max_height="550px",
            object_fit="contain",
            border_radius="md"
        ),
        rx.icon(tag="arrow_big_left", position="absolute", left="0.5em", top="50%", transform="translateY(-50%)", on_click=BlogViewState.anterior_imagen, cursor="pointer", box_size="2em"),
        rx.icon(tag="arrow_big_right", position="absolute", right="0.5em", top="50%", transform="translateY(-50%)", on_click=BlogViewState.siguiente_imagen, cursor="pointer", box_size="2em"),
        width="100%",
        max_width="600px",
        position="relative",
        border_radius="md",
        overflow="hidden"
    )

def _info_section() -> rx.Component:
    """Sección que muestra el título, precio y descripción."""
    return rx.vstack(
        rx.text(BlogViewState.post.title, size="7", font_weight="bold", margin_bottom="0.5em", text_align="left"),
        rx.text(BlogViewState.formatted_price, size="6", color="gray", text_align="left"),
        rx.text(BlogViewState.content, size="4", margin_top="1em", white_space="pre-wrap", text_align="left"),
        padding="1em",
        align="start",
        width="100%",
    )