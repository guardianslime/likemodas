# likemodas/blog/detail.py (CORREGIDO)

import reflex as rx
from ..auth.admin_auth import require_admin
from ..state import AppState, PostDetailData  # ✨ Importar el DTO
from .notfound import blog_post_not_found
from ..ui.carousel import Carousel

def _image_section(post: PostDetailData) -> rx.Component: # ✨ Aceptar el DTO como parámetro
    """Muestra las imágenes del post del admin."""
    return rx.box(
        Carousel.create(
            rx.foreach(
                post.image_urls,
                lambda image_url: rx.image(src=rx.get_upload_url(image_url), alt=post.title, width="100%", height="auto", object_fit="cover", border_radius="var(--radius-3)")
            ),
            show_arrows=True, show_indicators=True, infinite_loop=True, auto_play=True, width="100%"
        ),
        width="100%", max_width="800px", margin="auto", padding_y="1em"
    )

def _info_section(post: PostDetailData) -> rx.Component: # ✨ Aceptar el DTO como parámetro
    """Muestra la info del post del admin."""
    return rx.vstack(
        rx.text(post.title, size="7", font_weight="bold"),
        rx.text(post.price_cop, size="6", color="gray"),
        rx.text(post.content, size="4", margin_top="1em", white_space="pre-wrap"),
        rx.spacer(),
        rx.hstack(
            rx.button(rx.cond(post.publish_active, "Despublicar", "Publicar"), on_click=AppState.toggle_publish_status(post.id)),
            rx.link(rx.button("Editar Post", variant="soft"), href=f"/blog/{post.id}/edit"),
            rx.button("Eliminar Post", color_scheme="red", on_click=AppState.delete_post(post.id)),
            spacing="4", margin_top="2em"
        ),
        padding="1em", align="start", width="100%",
    )

@require_admin
def blog_post_detail_content() -> rx.Component:
    """Página que muestra el detalle de un post del admin."""
    return rx.center(
        rx.vstack(
            rx.heading("Detalle de mi Publicación", size="8", margin_bottom="1em"),
            rx.cond(
                AppState.post,
                # ✨ Pasar la variable de estado (que es un DTO) a los componentes hijos
                rx.grid(_image_section(AppState.post), _info_section(AppState.post), columns="2", spacing="4", align_items="start", width="100%", max_width="1120px"),
                blog_post_not_found()
            ),
            spacing="6", width="100%", padding="2em", align="center",
        ),
        width="100%",
    )