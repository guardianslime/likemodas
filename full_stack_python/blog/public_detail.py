# full_stack_python/blog/public_detail.py (CÓDIGO CORREGIDO Y COMPLETO)

import reflex as rx
import reflex_local_auth
from .state import BlogViewState
from .. import navigation
from ..navigation.device import NavDeviceState
from ..navigation.state import force_reload_go_to
from ..ui.base import fixed_color_mode_button
from ..ui.search_state import SearchState
from ..ui.nav import public_navbar # Importamos la public_navbar unificada

# Esta es la barra de navegación local, con el estilo correcto y la recarga forzada.
# ELIMINAMOS _detail_page_navbar() ya que usaremos public_navbar()

def standalone_public_layout(child: rx.Component) -> rx.Component:
    """Layout autónomo que usa la navbar local."""
    return rx.fragment(
        public_navbar(), # <--- CAMBIO: Ahora usa la public_navbar unificada
        rx.box(
            child,
            padding_y="2em",
            padding_top="6rem", # Asegura el padding correcto para la navbar fija
            width="100%",
            margin="0 auto",
        ),
        fixed_color_mode_button(),
    )

# --- PÁGINA DE DETALLE MODIFICADA ---
def blog_public_detail_page() -> rx.Component:
    """Página que muestra el detalle de una publicación pública."""
    
    # Este es el contenido principal de la página (la imagen y la información).
    content_grid = rx.cond(
        BlogViewState.has_post,
        rx.grid(
            _image_section(),
            _info_section(),
            columns={"base": "1", "md": "2"},
            spacing="4",
            align_items="start",
            width="100%",
            max_width="1120px", # Se añade un ancho máximo
        ),
        rx.center(rx.text("Publicación no encontrada.", color="red"))
    )
    
    # ✨ CAMBIO: Se envuelve el contenido en una estructura centrada con título.
    # Esto imita el layout de la página de la galería.
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


# --- Componentes de la sección de imagen e información (SIN CAMBIOS) ---
def _image_section() -> rx.Component:
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
            border_radius="md",
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
    return rx.vstack(
        rx.text(BlogViewState.post.title, size="7", font_weight="bold", margin_bottom="0.5em", text_align="left"),
        rx.text(BlogViewState.formatted_price, size="6", color="gray", text_align="left"),
        rx.text(BlogViewState.content, size="4", margin_top="1em", white_space="pre-wrap", text_align="left"),
        padding="1em",
        align="start",
        width="100%",
    )
