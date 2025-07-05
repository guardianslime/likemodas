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
                    # 1. La condición ahora revisa si la lista 'post.images' tiene contenido.
                    # 2. Se usa la primera imagen de la lista 'post.images[0].filename' para la miniatura.
                    rx.cond(
                        post.images,
                        rx.image(
                            src=rx.get_upload_url(post.images[0].filename),
                            width="100%",
                            height="200px",
                            object_fit="cover"
                        )
                    ),
                    rx.heading(post.title, size="4", margin_top="0.5em"),
                ),
                spacing="2",
                direction="column"
            ),
            href=post_detail_url
        ), 
        as_child=True,
        width="100%",
    )

def article_public_list_component(columns:int=3, spacing:int=5, limit:int=100) -> rx.Component:
    return rx.grid(
        rx.foreach(state.ArticlePublicState.posts, article_card_link),
        columns=f'{columns}',
        spacing= f'{spacing}',
        width="100%",
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