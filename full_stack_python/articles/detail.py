# full_stack_python/articles/detail.py (CORREGIDO Y ROBUSTO)

import reflex as rx
from ..ui.base import base_page
from . import state
from ..blog.notfound import blog_post_not_found

def article_detail_page() -> rx.Component:
    # --- CORRECCIÓN CLAVE ---
    # La condición ahora verifica toda la cadena de objetos:
    # que exista el post, su userinfo y el usuario dentro de userinfo.
    my_child = rx.cond(
        (state.ArticlePublicState.post) &
        (state.ArticlePublicState.post.userinfo) &
        (state.ArticlePublicState.post.userinfo.user),

        # Si todo existe, se muestra el contenido del post.
        rx.vstack(
            rx.hstack(
                rx.heading(state.ArticlePublicState.post.title, size="9"),
                align='end'
            ),
            rx.text("By ", state.ArticlePublicState.post.userinfo.user.username),
            
            # Se muestra la fecha de publicación solo si existe.
            rx.cond(
                state.ArticlePublicState.post.publish_date,
                rx.text(state.ArticlePublicState.post.publish_date.to_string()),
                rx.text("Fecha no disponible")
            ),

            rx.text(
                state.ArticlePublicState.post.content,
                white_space='pre-wrap'
            ),
            spacing="5",
            align="center",
            min_height="85vh",
        ),
        # Si algo falla en la condición, se muestra la página de "no encontrado".
        blog_post_not_found()
    )
    return base_page(my_child)