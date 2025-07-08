# full_stack_python/blog/detail.py (CORRECCIÓN FINAL)

import reflex as rx
from ..ui.base import base_page
from . import state
from .notfound import blog_post_not_found

def blog_post_detail_page() -> rx.Component:
    # Ya NO creamos el link aquí.

    my_child = rx.cond(
        (state.BlogPostState.post) &
        (state.BlogPostState.post.userinfo) &
        (state.BlogPostState.post.userinfo.user),
        
        rx.vstack(
            rx.hstack(
                rx.heading(state.BlogPostState.post.title, size="9"),
                
                # --- CORRECCIÓN CLAVE ---
                # Creamos el componente rx.link aquí, DENTRO de la condición,
                # donde es seguro acceder a la URL de edición.
                rx.link("Editar", href=state.BlogPostState.blog_post_edit_url),

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
                    state.BlogPostState.post.publish_date.to_string()
                ),
                rx.text("Este post aún no ha sido publicado.")
            ),

            rx.divider(width="100%"),
            
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