import reflex as rx
from ..ui.base import base_page
from .state import BlogPostState

def blog_post_detail_page() -> rx.Component:
    return base_page(
        rx.cond(
            BlogPostState.post,
            rx.vstack(
                rx.heading(BlogPostState.post.title),
                rx.text("por ", BlogPostState.post.userinfo.email),
                rx.grid(
                    rx.foreach(
                        BlogPostState.post.images,
                        lambda img: rx.image(src=f"/_upload/{img.filename}")
                    ),
                    columns="3"
                ),
                rx.text(BlogPostState.post.content)
            ),
            rx.spinner(size="3")
        ),
        on_mount=BlogPostState.get_post_detail
    )