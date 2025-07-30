# likemodas/blog/list.py (CORREGIDO)
import reflex as rx
# --- ✨ CAMBIO: Se importa el decorador de admin ---
from ..auth.admin_auth import require_admin
from ..ui.base import base_page
from ..models import BlogPostModel
from .. import navigation
from .state import BlogPostState

# (La función _gallery_card no cambia)
def _gallery_card(post: BlogPostModel) -> rx.Component:
    return rx.link(
        rx.card(
            rx.inset(
                # --- LÍNEA CORREGIDA ---
                rx.cond(
                    # Usa 'image_urls' y la función rx.length()
                    post.image_urls & (rx.length(post.image_urls) > 0),
                    rx.image(
                        # --- LÍNEA CORREGIDA ---
                        src=post.image_urls, # Muestra la primera imagen de la lista
                        width="100%",
                        height="140px",
                        object_fit="cover",
                    ),
                    rx.box( # Fallback si no hay imágenes
                        rx.icon("image_off", size=48),
                        height="140px",
                        width="100%",
                        bg=rx.color("gray", 4),
                        display="flex",
                        align_items="center",
                        justify_content="center",
                    )
                )
            ),
            #... resto de la tarjeta con el título, etc.
            rx.text(post.title, weight="bold", as_="div", size="3", margin_bottom="1"),
            rx.text(post.content, as_="p", size="2", color_scheme="gray", trim="end", height="4.5em"),
        ),
        href=f"/blog-public/{post.id}",
        as_child=True, # Para que toda la tarjeta sea un enlace
        style={"text_decoration": "none"}
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