import reflex as rx 

from .. import navigation
from ..ui.base import base_page
from ..models import BlogPostModel
from . import state

def article_link(post: BlogPostModel):
    post_id = post.id
    if post_id is None:
        return rx.fragment("Not found")
    root_path = navigation.routes.BLOG_POSTS_ROUTE
    post_detail_url = f"{root_path}/{post_id}"
    return rx.card(
        rx.link(
            rx.flex(
                rx.box(
                    rx.heading("post.title"),
                ),
                spacing="2",
            ),
            href=post_detail_url
        ), 
        as_child=True
    )
   

def article_list_item(post: BlogPostModel):
    return rx.box(
        article_link(    
            rx.heading(post.title),
            post
        ),
        padding="1em"
    )

# def foreach_callback(text):
#     return rx.box(rx.text(text))

def article_public_list_page() -> rx.Component:
    return base_page(
        rx.vstack(
            rx.heading("Blog Posts", size="5"),
            rx.link(
                rx.button("New Post"),
                href=navigation.routes.BLOG_POST_ADD_ROUTE
            ),
            # rx.foreach(["abc", "abc", "cde"], foreach_callback),
            rx.foreach(state.ArticlePublicState.posts, article_list_item),          
            spacing="5",
            align="center",
            min_height="85vh",
        )
    )