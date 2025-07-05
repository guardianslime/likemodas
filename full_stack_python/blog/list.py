import reflex as rx
import reflex_local_auth
from ..ui.base import base_page
from ..models import BlogPostModel
from .state import BlogPostState

def blog_post_list_item(post: BlogPostModel):
    return rx.link(rx.card(rx.text(post.title)), href=f"/blog/{post.id}/edit")

@reflex_local_auth.require_login
def blog_post_list_page() -> rx.Component:
    return base_page(
        rx.vstack(
            rx.heading("Mis Publicaciones", size="8"),
            rx.link(rx.button("Crear Nueva Publicación"), href="/blog/add"),
            rx.foreach(BlogPostState.posts, blog_post_list_item),
            spacing="5", align="center", min_height="85vh",
        ),
        on_mount=BlogPostState.load_posts
    )