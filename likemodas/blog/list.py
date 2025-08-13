# likemodas/blog/list.py (CORREGIDO)

import reflex as rx
from ..auth.admin_auth import require_admin
from ..state import AppState, ProductCardData
from .. import navigation

def _gallery_card(post: ProductCardData) -> rx.Component:
    """Tarjeta de producto para la galería, ahora sin `post.content`."""
    return rx.link(
        rx.card(
            rx.inset(
                rx.cond(
                    post.image_urls,
                    rx.image(src=rx.get_upload_url(post.image_urls[0]), width="100%", height="140px", object_fit="cover"),
                    rx.box(
                        rx.icon("image_off", size=48), height="140px", width="100%", bg=rx.color("gray", 4),
                        display="flex", align_items="center", justify_content="center",
                    )
                )
            ),
            rx.text(post.title, weight="bold", as_="div", size="3", margin_bottom="1"),
            # ✨ LÍNEA ELIMINADA: Se quitó rx.text(post.content, ...) que causaba el error.
            # La galería no necesita mostrar la descripción completa.
        ),
        href=f"{navigation.routes.BLOG_PUBLIC_DETAIL_ROUTE}/{post.id}",
        as_child=True, style={"text_decoration": "none"}
    )

@require_admin
def blog_post_list_content() -> rx.Component:
    """Página que muestra la galería de posts del admin."""
    return rx.center(
        rx.vstack(
            rx.heading("Mis Publicaciones", size="8", margin_bottom="1em"),
            rx.input(
                placeholder="Buscar por nombre...",
                value=AppState.search_query_admin_posts,
                on_change=AppState.set_search_query_admin_posts,
                width="100%", max_width="400px", margin_bottom="1.5em",
            ),
            rx.cond(
                AppState.filtered_admin_posts,
                rx.grid(
                    rx.foreach(AppState.filtered_admin_posts, _gallery_card),
                    columns="4", spacing="6", width="100%", max_width="1200px",
                ),
                rx.center(rx.text("No se encontraron publicaciones."), padding_y="4em")
            ),
            spacing="6", width="100%", padding="2em", align="center"
        ),
        width="100%"
    )