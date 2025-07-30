# likemodas/blog/detail.py (CORREGIDO)
import reflex as rx
# --- ✨ CAMBIO: Se importa el decorador de admin ---
from ..auth.admin_auth import require_admin
from ..ui.base import base_page
from .state import BlogPostState
from .notfound import blog_post_not_found
from..ui.carousel import Carousel  # <--- LÍNEA CORREGID

# (Las funciones _image_section y _info_section no cambian)
def _image_section() -> rx.Component:
    """
    Muestra las imágenes del post en un carrusel.
    """
    return rx.box(
        # Usamos Carousel.create() para instanciar el componente
        Carousel.create(
            # rx.foreach itera sobre la lista de URLs de las imágenes del estado
            rx.foreach(
                BlogPostState.post.image_urls,  # <--- USA EL NOMBRE CORRECTO
                lambda image_url: rx.image(
                    src=image_url,
                    alt=BlogPostState.post.title,
                    width="100%",
                    height="auto",
                    object_fit="cover",
                    border_radius="var(--radius-3)",
                )
            ),
            # Propiedades del carrusel
            show_arrows=True,
            show_indicators=True,
            infinite_loop=True,
            auto_play=True,
            width="100%"
        ),
        width="100%",
        max_width="800px",
        margin="auto",
        padding_y="1em"
    )

def _info_section() -> rx.Component:
    return rx.vstack(
        rx.text(BlogPostState.post.title, size="7", font_weight="bold", margin_bottom="0.5em", text_align="left"),
        rx.text(BlogPostState.formatted_price, size="6", color="gray", text_align="left"),
        rx.text(BlogPostState.post.content, size="4", margin_top="1em", white_space="pre-wrap", text_align="left"),
        rx.spacer(),
        rx.hstack(
            # ✨ --- NUEVO BOTÓN AÑADIDO --- ✨
            rx.button(
                rx.cond(BlogPostState.post.publish_active, "Despublicar", "Publicar"),
                on_click=BlogPostState.toggle_publish_status(BlogPostState.post.id),
                color_scheme=rx.cond(BlogPostState.post.publish_active, "yellow", "green")
            ),
            rx.link(rx.button("Editar Post", variant="soft"), href=BlogPostState.blog_post_edit_url),
            rx.button("Eliminar Post", color_scheme="red", on_click=BlogPostState.delete_post(BlogPostState.post.id)),
            spacing="4",
            margin_top="2em"
        ),
        padding="1em",
        align="start",
        width="100%",
    )


# --- ✨ CAMBIO: Se usa el decorador de admin ---
@require_admin
def blog_post_detail_page() -> rx.Component:
    """Página que muestra el detalle de un post del admin."""
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