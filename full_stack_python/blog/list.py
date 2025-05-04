import reflex as rx 

from .. import navigation
from ..ui.base import base_page

from . import state, model

def blog_post_list_item(post: model.BlogPostModel):
    return rx.box(
        rx.heading(post.title),
        padding="1em"
    )

# def foreach_callback(text):
#     return rx.box(rx.text(text))

def blog_post_list_page() -> rx.Component:
    return base_page(
        rx.vstack(
            rx.heading("Blog Posts", size="5"),
            # rx.foreach(["abc", "abc", "cde"], foreach_callback),
            rx.foreach(state.BlogPostState.posts,
            blog_post_list_item),
            spacing="5",
            align="center",
            min_height="85vh",
        )
    )