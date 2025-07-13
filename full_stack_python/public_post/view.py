import reflex as rx
from full_stack_python.ui.base import base_page
from full_stack_python.public_post.state import BlogViewState

def public_post_detail_page() -> rx.Component:
    """
    Página que muestra el detalle de una publicación pública,
    con un layout responsivo explícito para evitar conflictos.
    """
    # El contenido de la página ahora usa un fragmento que elige el layout
    # correcto según el tamaño de la pantalla.
    my_child = rx.box(
        rx.cond(
            BlogViewState.has_post,
            rx.fragment(
                # --- LAYOUT PARA ESCRITORIO ---
                rx.desktop_only(
                    rx.grid(
                        _image_section(),
                        _info_section(),
                        columns="1fr 1fr", # Dos columnas lado a lado
                        spacing="4",
                        align_items="start",
                        width="100%",
                    )
                ),
                # --- LAYOUT PARA MÓVIL Y TABLET ---
                rx.mobile_and_tablet(
                    rx.vstack(
                        _image_section(),
                        _info_section(),
                        spacing="4",
                        align_items="center", # Centrado para vista móvil
                        width="100%",
                    )
                ),
            ),
            # Mensaje si la publicación no se encuentra
            rx.center(rx.text("Publicación no encontrada.", color="red"))
        ),
        padding_y="2em",
        width="100%",
        max_width="1440px",
        margin="0 auto",
    )

    return base_page(
        my_child,
        on_mount=BlogViewState.on_load
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
            height="auto", # Altura automática para mantener la proporción
            max_height="550px", # Altura máxima para evitar que sea muy grande
            object_fit="contain",
            border_radius="md"
        ),
        # Flechas de navegación
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
        # Estilos del contenedor
        width="100%",
        max_width="600px",
        position="relative",
        border_radius="md",
        overflow="hidden"
    )


def _info_section() -> rx.Component:
    """Sección que muestra el título, precio y descripción."""
    return rx.vstack(
        rx.text(
            BlogViewState.post.title,
            size="7", # Un poco más grande para el título
            font_weight="bold",
            margin_bottom="0.5em",
            text_align="left", # Siempre alineado a la izquierda
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
        align="start", # Alinea todo el contenido a la izquierda
        width="100%",
    )