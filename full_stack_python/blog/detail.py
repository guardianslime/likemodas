# full_stack_python/blog/detail.py

import reflex as rx 
from ..ui.base import base_page
from .state import BlogPostState
from ..ui.components import not_found_component

def blog_post_detail_page() -> rx.Component:
    post = BlogPostState.post
    edit_link = rx.link("Editar", href=BlogPostState.blog_post_edit_url)
    
    detail_view = rx.vstack(
        rx.hstack(
            rx.heading(post.title, size="9"),
            edit_link,
            align='end', justify='between', width="100%"
        ),
        rx.text(
            "Publicado por: ", 
            rx.code(post.userinfo.user.username), " (", rx.code(post.userinfo.email), ")"
        ),
        rx.cond(
            post.publish_date,
            rx.text("Fecha de publicación: ", post.publish_date.to_string()),
            rx.text("Este post aún no ha sido publicado.")
        ),
        rx.divider(width="100%"),

        # --- CORRECCIÓN FINAL ---
        # Envolvemos TODA la galería en un rx.cond.
        rx.grid(
            rx.foreach(
                BlogPostState.post_images, # <-- Usa la nueva propiedad segura
                lambda img: rx.image(
                    src=f"/_upload/{img.filename}", 
                    width="100%", height="auto", border_radius="md"
                )
            ),
            columns="3", spacing="4", width="100%", margin_y="1em",
        ),

        rx.text(post.content, white_space='pre-wrap'),
        spacing="5", align="start", min_height="85vh", width="100%"
    )

    return base_page(
        rx.cond(
            post,
            detail_view,
            not_found_component(title="Publicación no encontrada")
        )
    )