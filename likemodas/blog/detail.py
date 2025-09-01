# likemodas/blog/detail.py (CORREGIDO)

import reflex as rx
from ..auth.admin_auth import require_admin
from ..state import AppState
from .notfound import blog_post_not_found
from ..ui.carousel import Carousel

def _image_section() -> rx.Component:
    """Muestra las imágenes del post del admin usando el sistema de variantes."""
    return rx.box(
        Carousel.create(
            # --- ✨ CORRECCIÓN AQUÍ ✨ ---
            rx.foreach(
                # Itera sobre las variantes para obtener las URLs de las imágenes
                AppState.post.variants,
                lambda variant: rx.image(
                    src=rx.get_upload_url(variant.get("image_url", "")), 
                    alt=AppState.post.title, 
                    width="100%", height="auto", 
                    object_fit="cover", 
                    border_radius="var(--radius-3)"
                )
            ),
            show_arrows=True, show_indicators=True, infinite_loop=True, auto_play=True, width="100%"
        ),
        width="100%", max_width="800px", margin="auto", padding_y="1em"
    )

def _info_section() -> rx.Component:
    """Muestra la info del post del admin."""
    return rx.vstack(
        rx.text(AppState.post.title, size="7", font_weight="bold"),
        rx.text(AppState.post.price_cop, size="6", color="gray"),
        rx.text(AppState.post.content, size="4", margin_top="1em", white_space="pre-wrap"),
        rx.spacer(),
        rx.hstack(
            rx.button(rx.cond(AppState.post.publish_active, "Despublicar", "Publicar"), on_click=AppState.toggle_publish_status(AppState.post.id)),
            rx.link(rx.button("Editar Post", variant="soft"), href=AppState.blog_post_edit_url),
            rx.button("Eliminar Post", color_scheme="red", on_click=AppState.delete_post(AppState.post.id)),
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
                rx.grid(_image_section(), _info_section(), columns="2", spacing="4", align_items="start", width="100%", max_width="1120px"),
                blog_post_not_found()
            ),
            spacing="6", width="100%", padding="2em", align="center",
        ),
        width="100%",
    )

