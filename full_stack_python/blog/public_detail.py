# full_stack_python/blog/public_detail.py (CÓDIGO CORREGIDO Y UNIFICADO)

import reflex as rx
from .state import BlogViewState
# ✨ CAMBIOS EN IMPORTS: Importamos los nuevos componentes unificados
from ..ui.nav import public_navbar
from ..ui.base import fixed_color_mode_button

# --- LAYOUT AUTÓNOMO MODIFICADO ---
def standalone_public_layout(child: rx.Component) -> rx.Component:
    """
    Un layout completamente independiente que ahora usa los componentes de UI unificados.
    """
    return rx.fragment(
        public_navbar(),          # <--- ✨ CAMBIO: Usa la nueva navbar superior
        rx.box(
            child,
            padding_y="2em",
            # Se ajusta el padding para que el contenido no se oculte debajo de la navbar
            padding_top="6rem", 
            width="100%",
            max_width="1440px",
            margin="0 auto",
        ),
        fixed_color_mode_button(), # <--- ✨ CAMBIO: Usa el nuevo botón de tema fijo
    )

# --- PÁGINA DE DETALLE (SIN CAMBIOS EN SU LÓGICA INTERNA) ---
def blog_public_detail_page() -> rx.Component:
    """
    Página que muestra el detalle de una publicación pública.
    Sigue usando su propio layout aislado, pero ahora con componentes consistentes.
    """
    content_grid = rx.cond(
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
    )
    
    return standalone_public_layout(content_grid)


# --- Componentes de la sección de imagen e información (SIN CAMBIOS) ---

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