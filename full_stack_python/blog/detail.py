# full_stack_python/blog/detail.py

import reflex as rx 
from ..ui.base import base_page
from . import state
from .notfound import blog_post_not_found

def blog_post_detail_page() -> rx.Component:
    edit_link = rx.link("Editar", href=state.BlogPostState.blog_post_edit_url)

    # La corrección principal está aquí. Se verifica que todos los objetos anidados
    # (post, post.userinfo, post.userinfo.user) existan antes de renderizar.
    my_child = rx.cond(
        (state.BlogPostState.post) & 
        (state.BlogPostState.post.userinfo) & 
        (state.BlogPostState.post.userinfo.user),
        
        # Si todo existe, se muestra el contenido del post.
        rx.vstack(
            rx.hstack(
                rx.heading(state.BlogPostState.post.title, size="9"),
                edit_link,
                align='end',
                justify='between',
                width="100%"
            ),
            
            # --- CORRECCIÓN CLAVE ---
            # Se reemplaza .to_string() por atributos reales del modelo como .username y .email.
            rx.text(
                "Publicado por: ", 
                rx.code(state.BlogPostState.post.userinfo.user.username),
                " (",
                rx.code(state.BlogPostState.post.userinfo.email),
                ")"
            ),
            
            # Se muestra la fecha de publicación solo si existe para evitar errores.
            rx.cond(
                state.BlogPostState.post.publish_date,
                rx.text(
                    "Fecha de publicación: ",
                    state.BlogPostState.post.publish_date.to_string() # .to_string() en objetos datetime sí es válido.
                ),
                rx.text("Este post aún no ha sido publicado.")
            ),

            rx.divider(width="100%"),
            
            # El contenido del post.
            rx.text(
                state.BlogPostState.post.content,
                white_space='pre-wrap'
            ),
            
            spacing="5",
            align="start", # Alinear a la izquierda para mejor legibilidad.
            min_height="85vh",
            width="100%"
        ),
        
        # Si algo falla en la condición, se muestra la página de "no encontrado".
        blog_post_not_found()
    )
    
    return base_page(my_child)