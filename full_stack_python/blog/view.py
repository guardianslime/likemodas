import reflex as rx
from .state import BlogViewState

def blog_post_view_page():
    return rx.cond(
        BlogViewState.post,
        rx.vstack(
            rx.heading(BlogViewState.post.title),
            rx.text(f"${BlogViewState.post.price:.2f}"),
            rx.foreach(
                BlogViewState.post.images,
                lambda img: rx.image(src=rx.get_upload_url(img), width="400px")
            ),
            rx.text(BlogViewState.post.content, white_space="pre-wrap"),
            padding="2em",
            spacing="4"
        ),
        rx.text("Publicación no encontrada.")
    )
