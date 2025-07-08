import reflex as rx
from .state import BlogPublicState

def blog_public_page():
    return rx.vstack(
        rx.heading("Publicaciones"),
        rx.foreach(
            BlogPublicState.posts,
            lambda post: rx.box(
                rx.link(
                    rx.image(src=rx.get_upload_url(post.images[0]), width="200px"),
                    href=f"/blog/public/{post.id}" # <- ruta corregida
                ),
                rx.text(post.title),
                rx.text(f"${post.price:.2f}"),
                padding="1em",
                border="1px solid #ccc",
                border_radius="8px",
                margin="0.5em"
            )
        ),
        padding="2em"
    )
