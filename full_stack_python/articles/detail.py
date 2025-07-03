# full_stack_python/articles/detail.py

import reflex as rx
from ..ui.base import base_page
from . import state
from ..blog.notfound import blog_post_not_found

def article_detail_page() -> rx.Component:
    """Página de detalle del artículo, ahora mostrando la imagen principal."""
    my_child = rx.cond(
        state.ArticlePublicState.post,
        rx.vstack(
            rx.heading(state.ArticlePublicState.post.title, size="9"),
            # --- CORRECCIÓN: Se muestra la imagen del post ---
            rx.cond(
                state.ArticlePublicState.post.image_url,
                rx.image(
                    src=state.ArticlePublicState.post.image_url,
                    width="100%",
                    max_width="48em",
                    height="auto",
                    margin_y="1.5em",
                    border_radius="0.75rem",
                    box_shadow="lg"
                )
            ),
            rx.text("Por ", state.ArticlePublicState.post.userinfo.user.username),
            # ... (resto de los detalles)
        ),
        blog_post_not_found()
    )
    return base_page(my_child)