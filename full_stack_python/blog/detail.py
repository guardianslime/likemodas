# full_stack_python/blog/detail.py

import reflex as rx 
from ..ui.base import base_page
from . import state
from .notfound import blog_post_not_found

def blog_post_detail_page() -> rx.Component:
    edit_link = rx.link("Editar", href=state.BlogPostState.blog_post_edit_url)
    
    my_child = rx.cond(
        (state.BlogPostState.post) & 
        (state.BlogPostState.post.userinfo) & 
        (state.BlogPostState.post.userinfo.user),
        
        rx.vstack(
            rx.hstack(
                rx.heading(state.BlogPostState.post.title, size="9"),
                edit_link,
                align='end',
                justify='between',
                width="100%"
            ),
            
            rx.text(
                "Publicado por: ", 
                rx.code(state.BlogPostState.post.userinfo.user.username),
                " (",
                rx.code(state.BlogPostState.post.userinfo.email),
                ")"
            ),
            
            rx.cond(
                state.BlogPostState.post.publish_date,
                rx.text(
                    "Fecha de publicación: ",
                    # Usamos .to_string() para mostrar la fecha de forma segura
                    state.BlogPostState.post.publish_date.to_string()
                ),
                rx.text("Este post aún no ha sido publicado.")
            ),

            rx.divider(width="100%"),
            
            # --- ¡CORRECCIÓN AQUÍ! ---
            # Usamos la nueva variable 'image_preview_url'
            rx.cond(
                state.BlogPostState.image_preview_url != "",
                rx.image(
                    src=state.BlogPostState.image_preview_url, 
                    width="100%", 
                    max_width="600px"
                )
            ),
            
            rx.text(
                state.BlogPostState.post.content,
                white_space='pre-wrap'
            ),
            
            spacing="5",
            align="start",
            min_height="85vh",
            width="100%"
        ),
        
        blog_post_not_found()
    )
    
    return base_page(my_child)