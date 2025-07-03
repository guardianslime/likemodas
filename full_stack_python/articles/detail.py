# full_stack_python/articles/detail.py

import reflex as rx
from ..ui.base import base_page
from . import state
from ..blog.notfound import blog_post_not_found

def article_detail_page() -> rx.Component:
    """Página de detalle del artículo, ahora mostrando la imagen principal."""
    # --- CORRECCIÓN: Se añade una condición más robusta para evitar errores. ---
    my_child = rx.cond(
        (state.ArticlePublicState.post) & 
        (state.ArticlePublicState.post.userinfo) & 
        (state.ArticlePublicState.post.userinfo.user),
        rx.vstack(
            rx.heading(state.ArticlePublicState.post.title, size="9"),
            rx.cond(
                state.ArticlePublicState.post.image_url,
                rx.image(
                    src=state.ArticlePublicState.post.image_url,
                    width="100%", max_width="48em", height="auto",
                    margin_y="1.5em", border_radius="0.75rem", box_shadow="lg"
                )
            ),
            rx.text(
                "Por ", 
                rx.code(state.ArticlePublicState.post.userinfo.user.username), 
                " | Publicado el: ",
                state.ArticlePublicState.post.publish_date.to_string(),
                size="4"
            ),
            rx.divider(margin_y="1em"),
            rx.text(
                state.ArticlePublicState.post.content,
                white_space='pre-wrap'
            ),
            spacing="5",
            align="start",
            min_height="85vh",
        ),
        blog_post_not_found()
    )
    return base_page(my_child)