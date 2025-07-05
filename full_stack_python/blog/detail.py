# full_stack_python/blog/detail.py

import reflex as rx 
from ..ui.base import base_page
# --- ¡CORRECCIÓN! ---
from .state import BlogPostState
from ..ui.components import not_found_component

def blog_post_detail_page() -> rx.Component:
    edit_link = rx.link("Editar", href=BlogPostState.blog_post_edit_url)
    
    my_child = rx.cond(
        BlogPostState.post,
        rx.vstack(
            rx.hstack(
                rx.heading(BlogPostState.post.title, size="9"),
                edit_link,
                align='end',
                justify='between',
                width="100%"
            ),
            rx.text(
                "Publicado por: ", 
                rx.code(BlogPostState.post.userinfo.user.username),
                " (",
                rx.code(BlogPostState.post.userinfo.email),
                ")"
            ),
            rx.cond(
                BlogPostState.post.publish_date,
                rx.text(
                    "Fecha de publicación: ",
                    BlogPostState.post.publish_date.to_string()
                ),
                rx.text("Este post aún no ha sido publicado.")
            ),
            rx.divider(width="100%"),
            rx.grid(
                rx.foreach(
                    BlogPostState.post.images,
                    lambda img: rx.image(
                        src=f"/_upload/{img.filename}", 
                        width="100%", 
                        height="auto", 
                        border_radius="md"
                    )
                ),
                columns="3",
                spacing="4",
                width="100%",
                margin_y="1em",
            ),
            rx.text(
                BlogPostState.post.content,
                white_space='pre-wrap'
            ),
            spacing="5",
            align="start",
            min_height="85vh",
            width="100%"
        ),
        not_found_component(title="Publicación no encontrada")
    )
    
    return base_page(my_child)