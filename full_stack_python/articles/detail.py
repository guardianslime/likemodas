import reflex as rx 
from ..ui.base import base_page
from . import state
from ..ui.components import not_found_component

def article_detail_page() -> rx.Component:
    post = state.ArticlePublicState.post
    
    article_view = rx.vstack(
        rx.hstack(rx.heading(post.title, size="9"), align='end'),
        rx.text("Por ", post.userinfo.user.username),
        rx.cond(post.publish_date, rx.text(post.publish_date.to_string())),
        rx.divider(),
        rx.grid(
            rx.foreach(
                state.ArticlePublicState.post_images,
                lambda img: rx.image(src=rx.get_upload_url(img.filename), width="100%", height="auto", border_radius="md")
            ),
            columns="3", spacing="4", width="100%", margin_y="1em",
        ),
        rx.text(post.content, white_space='pre-wrap'),
        spacing="5", align="start", min_height="85vh",
    )

    return base_page(
        rx.cond(post, article_view, not_found_component(title="Artículo No Encontrado")),
        on_mount=state.ArticlePublicState.get_post_detail # <-- AÑADIR
    )