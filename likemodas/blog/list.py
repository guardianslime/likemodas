# likemodas/blog/list.py (CORREGIDO)
import reflex as rx
# --- ✨ CAMBIO: Se importa el decorador de admin ---
from ..auth.admin_auth import require_admin
from ..ui.base import base_page
from ..models import BlogPostModel
from .. import navigation
from .state import BlogPostState

# (La función _gallery_card no cambia)
def _gallery_card(post: BlogPostModel):
    return rx.box(
        rx.link(
            rx.vstack(
                rx.box(
                    rx.cond(
                        post.images & (post.images.length() > 0),
                        rx.image(src=rx.get_upload_url(post.images[0]), width="100%", height="260px", object_fit="cover", border_radius="md", style={"_hover": {"transform": "scale(1.05)"}}),
                        rx.box("Sin imagen", width="100%", height="260px", bg="#eee", align="center", justify="center", display="flex", border_radius="md")
                    ),
                    position="relative",
                    width="100%",
                ),
                rx.heading(post.title, weight="bold", size="4", color=rx.color_mode_cond("black", "white"), margin_top="0.5em"),
                rx.text(rx.cond(post.price, "$" + post.price.to(str), "$0.00"), color=rx.color_mode_cond("black", "white"), size="4",),
                spacing="2",
                align="start",
                padding="0.5em"
            ),
            href=f"{navigation.routes.BLOG_POSTS_ROUTE}/{post.id}"
        ),
        bg=rx.color_mode_cond("#f9f9f9", "#1D1D1D"),
        border=rx.color_mode_cond("1px solid #e5e5e5", "1px solid #2a2a2a"),
        border_radius="lg",
        box_shadow="lg",
        overflow="hidden",
        transition="all 0.2s ease-in-out",
    )

# --- ✨ CAMBIO: Se usa el decorador de admin ---
@require_admin
def blog_post_list_page() -> rx.Component:
    """Página que muestra la galería de posts del admin."""
    return base_page(
        rx.center(
            rx.vstack(
                rx.heading("Mis Publicaciones", size="8", margin_bottom="1em"),
                
                # --- 👇 AÑADIR LA BARRA DE BÚSQUEDA 👇 ---
                rx.input(
                    placeholder="Buscar por nombre...",
                    value=BlogPostState.search_query,
                    on_change=BlogPostState.set_search_query,
                    width="100%",
                    max_width="400px",
                    margin_bottom="1.5em",
                ),

                rx.cond(
                    BlogPostState.filtered_posts, # <-- Usa la lista filtrada
                    rx.grid(
                        # --- 👇 USA LA LISTA FILTRADA AQUÍ 👇 ---
                        rx.foreach(BlogPostState.filtered_posts, _gallery_card),
                        columns={"base": "1", "sm": "2", "md": "3", "lg": "4"},
                        spacing="6",
                        width="100%",
                        max_width="1200px",
                    ),
                    rx.center(rx.text("No se encontraron publicaciones."), padding_y="4em")
                ),
                spacing="6",
                width="100%",
                padding="2em",
                align="center"
            ),
            width="100%"
        )
    )