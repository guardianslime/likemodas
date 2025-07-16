# full_stack_python/articles/detail.py
import reflex as rx
from ..ui.base import base_page
from ..auth.state import SessionState
from ..models import BlogPostModel
from typing import Optional

class ArticleDetailState(SessionState):
    post: Optional[BlogPostModel] = None
    img_idx: int = 0

    @rx.var
    def article_id(self) -> str:
        return self.router.page.params.get("article_id", "")

    @rx.var
    def imagen_actual(self) -> str:
        if self.post and self.post.images and len(self.post.images) > self.img_idx:
            return self.post.images[self.img_idx]
        return ""

    @rx.var
    def formatted_price(self) -> str:
        if self.post and self.post.price is not None:
            return f"${self.post.price:,.2f}"
        return "$0.00"

    @rx.event
    def on_load(self):
        try:
            pid = int(self.article_id)
        except (ValueError, TypeError):
            return
        with rx.session() as session:
            self.post = session.get(BlogPostModel, pid)
        self.img_idx = 0

    def siguiente_imagen(self):
        if self.post and self.post.images:
            self.img_idx = (self.img_idx + 1) % len(self.post.images)

    def anterior_imagen(self):
        if self.post and self.post.images:
            self.img_idx = (self.img_idx - 1 + len(self.post.images)) % len(self.post.images)

def _image_section() -> rx.Component:
    return rx.box(
        rx.image(
            src=rx.cond(
                ArticleDetailState.imagen_actual != "",
                rx.get_upload_url(ArticleDetailState.imagen_actual),
                "/no_image.png"
            ),
            width="100%", height="auto", max_height="550px", object_fit="contain", border_radius="md",
        ),
        rx.icon(tag="arrow_big_left", position="absolute", left="0.5em", top="50%", transform="translateY(-50%)", on_click=ArticleDetailState.anterior_imagen, cursor="pointer", box_size="2em"),
        rx.icon(tag="arrow_big_right", position="absolute", right="0.5em", top="50%", transform="translateY(-50%)", on_click=ArticleDetailState.siguiente_imagen, cursor="pointer", box_size="2em"),
        width="100%", max_width="600px", position="relative", border_radius="md", overflow="hidden"
    )

def _info_section() -> rx.Component:
    return rx.vstack(
        rx.text(ArticleDetailState.post.title, size="7", font_weight="bold", margin_bottom="0.5em", text_align="left"),
        rx.text(ArticleDetailState.formatted_price, size="6", color="gray", text_align="left"),
        rx.text(ArticleDetailState.post.content, size="4", margin_top="1em", white_space="pre-wrap", text_align="left"),
        padding="1em", align="start", width="100%",
    )

def article_detail_page() -> rx.Component:
    content_grid = rx.cond(
        ArticleDetailState.post,
        rx.grid(
            _image_section(), _info_section(),
            columns={"base": "1", "md": "2"},
            spacing="4", align_items="start", width="100%", max_width="1120px",
        ),
        rx.center(rx.text("Publicación no encontrada.", color="red"))
    )
    page_content = rx.center(
        rx.vstack(
            rx.heading("Detalle del Producto", size="8", margin_bottom="1em"),
            content_grid,
            spacing="6", width="100%", padding="2em", align="center",
        ),
        width="100%",
    )
    return base_page(page_content)