# full_stack_python/blog/detail.py

import reflex as rx 
from ..ui.base import base_page
from . import state
from .notfound import blog_post_not_found

def blog_post_detail_page() -> rx.Component:
    edit_link = rx.link("Editar", href=state.BlogPostState.blog_post_edit_url)
    
    my_child = rx.cond(
        (state.BlogPostState.post) & (state.BlogPostState.post.userinfo) & (state.BlogPostState.post.userinfo.user),
        rx.vstack(
            rx.hstack(
                rx.heading(state.BlogPostState.post.title, size="9"),
                # --- NUEVO: Botón para editar ---
                edit_link,
                align='end', justify='between', width="100%"
            ),
            rx.text(...), # autor
            rx.text(...), # fecha
            rx.divider(width="100%"),

            # --- CAMBIO: Mostrar galería de imágenes ---
            rx.grid(
                rx.foreach(
                    state.BlogPostState.post.images,
                    lambda img: rx.image(src=f"/_upload/{img.filename}", width="100%", height="auto", border_radius="md")
                ),
                columns="3",
                spacing="4",
                width="100%"
            ),

            rx.text(state.BlogPostState.post.content, white_space='pre-wrap'),
            spacing="5", align="start", min_height="85vh", width="100%"
        ),
        blog_post_not_found()
    )
    return base_page(my_child)