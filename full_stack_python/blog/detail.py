# full_stack_python/blog/detail.py (CORREGIDO)

import reflex as rx
from ..ui.base import base_page
from . import state
from .notfound import blog_post_not_found

def blog_post_detail_page() -> rx.Component:
    return base_page(
        rx.cond(
            state.BlogPostState.post,
            rx.vstack(
                rx.hstack(
                    rx.heading(state.BlogPostState.post.title, size="9"),
                    rx.spacer(),
                    rx.link("Editar", href=state.BlogPostState.blog_post_edit_url, button=True, variant="soft"),
                    justify="between",
                    width="100%"
                ),
                rx.hstack(
                    rx.badge(
                        rx.cond(
                            state.BlogPostState.post.publish_active,
                            "Publicado", "Borrador"
                        ),
                        color_scheme=rx.cond(
                            state.BlogPostState.post.publish_active,
                            "green", "gray"
                        )
                    ),
                    # --- ✨ CORRECCIÓN AQUÍ ✨ ---
                    # Usamos la nueva propiedad 'publish_date_formatted'
                    rx.cond(
                        state.BlogPostState.post.publish_date,
                        rx.text(f"Publicado el: {state.BlogPostState.post.publish_date_formatted}")
                    ),
                    spacing="4"
                ),
                rx.divider(),
                rx.markdown(state.BlogPostState.post.content), # Usamos rx.markdown para renderizar contenido
                spacing="5",
                align="start",
                width="100%",
                max_width="960px",
                margin="auto",
            ),
            blog_post_not_found()
        )
    )