# full_stack_python/articles/list.py

import reflex as rx
from .. import navigation
from ..ui.base import base_page
from ..models import BlogPostModel
from . import state

def article_card_link(post: BlogPostModel):
    post_id = post.id
    if post_id is None:
        return rx.fragment("Not found")
    root_path = navigation.routes.ARTICLE_LIST_ROUTE
    post_detail_url = f"{root_path}/{post_id}"
    
    return rx.card(
        rx.link(
            rx.flex(
                rx.box(
                    # --- ¡CORRECCIÓN AQUÍ! ---
                    # Muestra la primera imagen de la lista si existe.
                    rx.cond(
                        post.images,
                        rx.image(
                            src=rx.get_upload_url(post.images[0].filename),
                            width="100%",
                            height="200px",
                            object_fit="cover"
                        )
                    ),
                    rx.heading(post.title, margin_top="0.5em"),
                ),
                spacing="2",
                direction="column"
            ),
            href=post_detail_url
        ),
        as_child=True
    )

def article_public_list_component(columns:int=3, spacing:int=5, limit:int=100) -> rx.Component:
    return rx.grid(
        rx.foreach(state.ArticlePublicState.posts, article_card_link),
        columns=f'{columns}',
        spacing= f'{spacing}',
        on_mount=lambda: state.ArticlePublicState.set_limit_and_reload(limit)
    )

def article_public_list_page() -> rx.Component:
    return base_page(
        rx.box(
            rx.heading("Artículos Publicados", size="5"),
            article_public_list_component(),      
            min_height="85vh",
        )
    )