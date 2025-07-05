# full_stack_python/articles/list.py

import reflex as rx 
from .. import navigation
from ..ui.base import base_page
from ..models import BlogPostModel
from .state import ArticlePublicState

def article_card_link(post: BlogPostModel):
    post_id = post.id
    if post_id is None:
        return rx.fragment("Not found")
    root_path = navigation.routes.ARTICLE_LIST_ROUTE
    post_detail_url = f"{root_path}/{post_id}"
    return rx.link(
        rx.card(
            rx.vstack(
                rx.cond(
                    post.images,
                    rx.image(
                        src=rx.get_upload_url(post.images[0].filename),
                        width="100%",
                        height="200px",
                        object_fit="cover",
                    ),
                    # Placeholder si no hay imagen
                    rx.box(
                        rx.icon("image", size=48, color_scheme="gray"),
                        width="100%",
                        height="200px",
                        bg=rx.color("gray", 3),
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        border_radius="var(--radius-3)",
                    )
                ),
                rx.heading(post.title, size="4", margin_top="0.5em"),
                align_items="start",
            )
        ),
        href=post_detail_url,
        width="100%",
    )

def article_public_list_component(columns: int = 3) -> rx.Component:
    """Componente que muestra la lista de artículos públicos."""
    return rx.grid(
        rx.foreach(ArticlePublicState.posts, article_card_link),
        # --- ¡CORRECCIÓN AQUÍ! ---
        # Se cambia 'default' por 'initial' para la correcta definición de breakpoints.
        columns=rx.breakpoints(initial="1", sm="2", md=str(columns)),
        spacing="4",
        width="100%",
    )

def article_public_list_page() -> rx.Component:
    """Página completa de la lista de artículos."""
    return base_page(
        rx.box(
            rx.heading("Artículos Públicos", size="8"),
            rx.divider(margin_y="1.5em"),
            article_public_list_component(),
            min_height="85vh",
            max_width="1200px",
            margin="auto",
            padding="1em",
        ),
        on_mount=ArticlePublicState.load_posts
    )