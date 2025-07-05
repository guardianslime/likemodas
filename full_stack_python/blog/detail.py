# full_stack_python/articles/detail.py

import reflex as rx 
from ..ui.base import base_page
from . import state
from ..blog.notfound import blog_post_not_found

def article_detail_page() -> rx.Component:
    my_child = rx.cond(
        state.ArticlePublicState.post,
        rx.vstack(
            rx.hstack(
                rx.heading(state.ArticlePublicState.post.title, size="9"),
                align='end'
            ),
            rx.text("Por ", state.ArticlePublicState.post.userinfo.user.username),
            rx.cond(
                state.ArticlePublicState.post.publish_date,
                rx.text(state.ArticlePublicState.post.publish_date.to_string()),
            ),
            rx.divider(),

            # --- ¡CORRECCIÓN AQUÍ! ---
            # Muestra una galería con todas las imágenes del post.
            rx.grid(
                rx.foreach(
                    state.ArticlePublicState.post.images,
                    lambda img: rx.image(
                        src=rx.get_upload_url(img.filename),
                        width="100%",
                        height="auto",
                        border_radius="md"
                    )
                ),
                columns="3",
                spacing="4",
                width="100%",
                margin_y="1em",
            ),

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