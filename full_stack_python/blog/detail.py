import reflex as rx
from ..ui.base import base_page
from .state import BlogPostState
from .notfound import blog_post_not_found
from ..ui.carousel import carousel

# --- Componentes visuales (copiados y adaptados de articles/detail.py) ---
def _image_section() -> rx.Component:
    """Sección para el carrusel de imágenes del post, usando react-responsive-carousel."""
    return rx.box(
        rx.cond(
            BlogPostState.post.images & (BlogPostState.post.images.length() > 0),
            # Usamos el nuevo componente 'carousel'
            carousel(
                rx.foreach(
                    BlogPostState.post.images,
                    # Cada imagen es un hijo directo del carrusel
                    lambda image_url: rx.image(
                        src=rx.get_upload_url(image_url),
                        width="100%",
                        height="auto",
                        max_height="550px",
                        object_fit="contain",
                    )
                ),
                # Configuramos el carrusel
                show_indicators=True,
                infinite_loop=True,
                emulate_touch=True, # Clave para que funcione con el mouse
                show_thumbs=False,
                # ✨ AÑADE ESTA LÍNEA PARA DESACTIVAR LA REPRODUCCIÓN AUTOMÁTICA ✨
                auto_play=False,
            ),
            # Mensaje si no hay imágenes
            rx.image(
                src="/no_image.png",
                width="100%",
                height="auto",
                max_height="550px",
                object_fit="contain",
                border_radius="md",
            )
        ),
        width="100%",
        max_width="600px",
        position="relative",
    )

def _info_section() -> rx.Component:
    """Sección para la información y acciones del post."""
    return rx.vstack(
        rx.text(BlogPostState.post.title, size="7", font_weight="bold", margin_bottom="0.5em", text_align="left"),
        rx.text(BlogPostState.formatted_price, size="6", color="gray", text_align="left"),
        rx.text(BlogPostState.post.content, size="4", margin_top="1em", white_space="pre-wrap", text_align="left"),
        rx.spacer(),
        # --- ✨ Botones de Acción ✨ ---
        rx.hstack(
            rx.link(rx.button("Editar Post", variant="soft"), href=BlogPostState.blog_post_edit_url),
            rx.button(
                "Eliminar Post",
                color_scheme="red",
                on_click=BlogPostState.delete_post(BlogPostState.post.id)
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
    """Página que muestra el detalle de un post del usuario, con el nuevo diseño."""
    content_grid = rx.cond(
        BlogPostState.post,
        rx.grid(
            _image_section(),
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