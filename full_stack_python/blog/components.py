# full_stack_python/blog/components.py (nuevo archivo si no existe)

import reflex as rx
from full_stack_python.models import BlogPostModel


def BlogCard(post: BlogPostModel) -> rx.Component:
    return rx.box(
        rx.link(
            rx.vstack(
                rx.heading(post.title, size="5"),
                rx.text(post.publish_date_formatted, size="2", color="gray"),
                rx.text(post.content[:100] + "...", size="3"),
            ),
            href=f"/public-post/{post.id}",
        ),
        border="1px solid #ccc",
        border_radius="md",
        padding="1em",
        width="100%",
    )
