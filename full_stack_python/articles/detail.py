# full_stack_python/articles/detail.py

import reflex as rx 
from ..ui.base import base_page
from . import state
from ..blog.notfound import blog_post_not_found

def article_detail_page() -> rx.Component:
    my_child = rx.cond(
        state.ArticlePublicState.post,
        rx.vstack(
            rx.hstack(...), # título
            rx.text(...), # autor
            rx.text(...), # fecha

            # --- CAMBIO: Mostrar galería de imágenes ---
            rx.grid(
                rx.foreach(
                    state.ArticlePublicState.post.images,
                    lambda img: rx.image(src=f"/_upload/{img.filename}", width="100%", height="auto", border_radius="md")
                ),
                columns="3",
                spacing="4",
                width="100%"
            ),
            
            rx.text(state.ArticlePublicState.post.content, white_space='pre-wrap'),
            spacing="5", align="center", min_height="85vh",
        ),
        blog_post_not_found()
    )
    return base_page(my_child)