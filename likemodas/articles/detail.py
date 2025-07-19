import reflex as rx
from ..ui.base import base_page
# --- ✨ CORRECCIÓN AQUÍ ✨ ---
# Ya no se importa SessionState, ahora se importa el estado específico desde el archivo de estado.
from .state import ArticleDetailState

# La clase ArticleDetailState ha sido movida a articles/state.py

# --- Componentes visuales (copiados de blog/public_detail.py) ---
def _image_section() -> rx.Component:
    return rx.box(
        rx.image(
            src=rx.cond(
                ArticleDetailState.imagen_actual != "",
                rx.get_upload_url(ArticleDetailState.imagen_actual),
                "/no_image.png"
            ),
            width="100%",
            height="auto",
            max_height="550px",
            object_fit="contain",
            border_radius="md",
        ),
        rx.icon(tag="arrow_big_left", position="absolute", left="0.5em", top="50%", transform="translateY(-50%)", on_click=ArticleDetailState.anterior_imagen, cursor="pointer", box_size="2em"),
        rx.icon(tag="arrow_big_right", position="absolute", right="0.5em", top="50%", transform="translateY(-50%)", on_click=ArticleDetailState.siguiente_imagen, cursor="pointer", box_size="2em"),
        width="100%",
        max_width="600px",
        position="relative",
        border_radius="md",
        overflow="hidden"
    )

def _info_section() -> rx.Component:
    return rx.vstack(
        rx.text(ArticleDetailState.post.title, size="7", font_weight="bold", margin_bottom="0.5em", text_align="left"),
        rx.text(ArticleDetailState.formatted_price, size="6", color="gray", text_align="left"),
        rx.text(ArticleDetailState.post.content, size="4", margin_top="1em", white_space="pre-wrap", text_align="left"),
        padding="1em",
        align="start",
        width="100%",
    )

# --- Página de Detalle ---
def article_detail_page() -> rx.Component:
    """Página que muestra el detalle de una publicación, copiada de blog/public_detail.py."""
    content_grid = rx.cond(
        ArticleDetailState.post,
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
    
    return base_page(page_content)