import reflex as rx
from ..ui.base import base_page
from .state import BlogPostState
from .notfound import blog_post_not_found
# Se importa el nuevo componente de carrusel
from ..ui.carousel import swiper_carousel

# --- Componentes visuales (copiados y adaptados de articles/detail.py) ---
def _image_section() -> rx.Component:
    """Sección para el carrusel de imágenes del post."""
    return rx.box(
        rx.image(
            src=rx.cond(
                BlogPostState.imagen_actual != "",
                rx.get_upload_url(BlogPostState.imagen_actual),
                "/no_image.png"
            ),
            width="100%",
            height="auto",
            max_height="550px",
            object_fit="contain",
            border_radius="md",
        ),
        rx.icon(tag="arrow_big_left", position="absolute", left="0.5em", top="50%", transform="translateY(-50%)", on_click=BlogPostState.anterior_imagen, cursor="pointer", box_size="2em", z_index=2, color="white", bg="rgba(0,0,0,0.3)", border_radius="full", padding="0.2em"),
        rx.icon(tag="arrow_big_right", position="absolute", right="0.5em", top="50%", transform="translateY(-50%)", on_click=BlogPostState.siguiente_imagen, cursor="pointer", box_size="2em", z_index=2, color="white", bg="rgba(0,0,0,0.3)", border_radius="full", padding="0.2em"),
        width="100%",
        max_width="600px",
        position="relative",
        border_radius="md",
        overflow="hidden"
    )

def _info_section() -> rx.Component:
    """Sección para la información y acciones del post."""
    return rx.vstack(
        rx.text(BlogPostState.post.title, size="7", font_weight="bold", margin_bottom="0.5em", text_align="left"),
        rx.text(BlogPostState.formatted_price, size="6", color="gray", text_align="left"),
        rx.text(BlogPostState.post.content, size="4", margin_top="1em", white_space="pre-wrap", text_align="left"),
        rx.spacer(),
        # --- ✨ Botones de Acción con Diálogo de Confirmación ✨ ---
        rx.hstack(
            rx.link(rx.button("Editar Post", variant="soft"), href=BlogPostState.blog_post_edit_url),
            rx.alert_dialog.root(
                rx.alert_dialog.trigger(
                    rx.button("Eliminar Post", color_scheme="red")
                ),
                rx.alert_dialog.content(
                    rx.alert_dialog.title("Confirmar Eliminación"),
                    rx.alert_dialog.description(
                        "¿Estás seguro de que quieres eliminar esta publicación? Esta acción es irreversible."
                    ),
                    rx.flex(
                        rx.alert_dialog.cancel(
                            rx.button("Cancelar", variant="soft", color_scheme="gray"),
                        ),
                        rx.alert_dialog.action(
                            rx.button("Sí, eliminar", color_scheme="red", on_click=BlogPostState.handle_delete_confirm),
                        ),
                        spacing="3",
                        margin_top="1em",
                        justify="end",
                    ),
                ),
            ),
            spacing="4",
            margin_top="2em"
        ),
        padding="1em",
        align="start",
        width="100%",
    )

# --- Página de Detalle de Post para usuarios logueados ---
def blog_post_detail_page() -> rx.Component:
    """Página de detalle con el nuevo carrusel y diálogo de borrado."""
    content_grid = rx.cond(
        BlogPostState.post,
        rx.grid(
            # Se reemplaza _image_section por el nuevo carrusel
            swiper_carousel(image_urls=BlogPostState.post_image_urls),
            _info_section(),
            columns={"base": "1", "md": "2"},
            spacing="4",
            align_items="start",
            width="100%",
            max_width="1120px",
        ),
        blog_post_not_found()
    )

    return base_page(
        rx.center(
            rx.vstack(
                rx.heading("Detalle de mi Publicación", size="8", margin_bottom="1em"),
                content_grid,
                spacing="6",
                width="100%",
                padding="2em",
                align="center",
            ),
            width="100%",
        )
    )