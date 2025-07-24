# likemodas/blog/detail_components.py

import reflex as rx
from ..ui.carousel import carousel
from .state import BlogPostState

def _image_section() -> rx.Component:
    """Muestra las imágenes del producto."""
    return rx.box(
        rx.cond(
            BlogPostState.post.images & (BlogPostState.post.images.length() > 0),
            carousel(
                rx.foreach(
                    BlogPostState.post.images, 
                    lambda image_url: rx.image(
                        src=rx.get_upload_url(image_url), 
                        width="100%", 
                        height="auto", 
                        max_height="550px", 
                        object_fit="contain",
                    )
                ),
                show_indicators=True, 
                infinite_loop=True, 
                emulate_touch=True, 
                show_thumbs=False, 
                auto_play=False,
            ),
            rx.image(
                src="/no_image.png", 
                width="100%", 
                height="auto", 
                max_height="550px", 
                object_fit="contain", 
                border_radius="md",
            )
        ),
        width="100%",
        max_width="600px",
        position="relative",
    )

def _info_section() -> rx.Component:
    """Muestra la información del producto y los botones de acción."""
    return rx.vstack(
        rx.text(
            BlogPostState.post.title, 
            size="7", 
            font_weight="bold", 
            margin_bottom="0.5em", 
            text_align="left"
        ),
        rx.text(
            BlogPostState.formatted_price, 
            size="6", 
            color="gray", 
            text_align="left"
        ),
        rx.text(
            BlogPostState.post.content, 
            size="4", 
            margin_top="1em", 
            white_space="pre-wrap", 
            text_align="left"
        ),
        rx.spacer(),
        rx.hstack(
            rx.button(
                rx.cond(BlogPostState.post.publish_active, "Despublicar", "Publicar"),
                on_click=BlogPostState.toggle_publish_status(BlogPostState.post.id),
                color_scheme=rx.cond(BlogPostState.post.publish_active, "yellow", "green")
            ),
            rx.link(
                rx.button("Editar Post", variant="soft"), 
                href=BlogPostState.blog_post_edit_url
            ),
            rx.button(
                "Eliminar Post", 
                color_scheme="red", 
                on_click=BlogPostState.delete_post(BlogPostState.post.id)
            ),
            spacing="4",
            margin_top="2em"
        ),
        padding="1em",
        align="start",
        width="100%",
    )