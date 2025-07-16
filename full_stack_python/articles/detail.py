import reflex as rx
from ..ui.base import base_page
from . import state
from ..blog.notfound import blog_post_not_found

def article_detail_page() -> rx.Component:
    condition = (
        state.ArticlePublicState.post
        & state.ArticlePublicState.post.userinfo
        & state.ArticlePublicState.post.userinfo.user
    )
    my_child = rx.cond(
        condition,
        rx.vstack(
            rx.hstack(
                rx.heading(state.ArticlePublicState.post.title, size="9"),
                align="end"
            ),
            rx.text("By ", state.ArticlePublicState.post.userinfo.user.username),
            rx.cond(
                state.ArticlePublicState.post.publish_date,
                rx.text(state.ArticlePublicState.post.publish_date.to_string()),
                rx.fragment()
            ),
            rx.text(
                state.ArticlePublicState.post.content,
                white_space="pre-wrap"
            ),
            spacing="5",
            align="center",
            min_height="85vh",
        ),
        blog_post_not_found()
    )
    return base_page(my_child)
