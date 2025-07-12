from typing import Optional
import reflex as rx
from full_stack_python.models import BlogPostModel

class BlogViewState(rx.State):
    post: Optional[BlogPostModel] = None
    img_idx: int = 0

    @rx.var
    def post_id(self) -> str:
        # ✅ Compatibilidad Reflex 0.8.1: usar .url y acceder a .params
        return self.router.url.split("/")[-1]

    @rx.var
    def imagen_actual(self) -> str:
        if self.post and self.post.images and len(self.post.images) > self.img_idx:
            return self.post.images[self.img_idx]
        return ""

    @rx.var
    def max_img_idx(self) -> int:
        if self.post and self.post.images:
            return len(self.post.images) - 1
        return 0

    @rx.var
    def formatted_price(self) -> str:
        if self.post and self.post.price is not None:
            return f"${self.post.price:,.2f}"
        return "$0.00"

    @rx.var
    def content(self) -> str:
        if self.post and self.post.content:
            return self.post.content
        return ""

    @rx.var
    def has_post(self) -> bool:
        return self.post is not None

    @rx.event
    def on_load(self):
        try:
            pid = int(self.post_id)
        except ValueError:
            return
        with rx.session() as session:
            self.post = session.get(BlogPostModel, pid)
        self.img_idx = 0

    @rx.event
    def siguiente_imagen(self):
        if self.post and self.post.images:
            self.img_idx = (self.img_idx + 1) % len(self.post.images)

    @rx.event
    def anterior_imagen(self):
        if self.post and self.post.images:
            self.img_idx = (self.img_idx - 1 + len(self.post.images)) % len(self.post.images)

class BlogListState(rx.State):
    blog_posts: list[BlogPostModel] = []

    def load_posts(self):
        self.blog_posts = list(BlogPostModel.select().order_by(BlogPostModel.created_at.desc()))

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

