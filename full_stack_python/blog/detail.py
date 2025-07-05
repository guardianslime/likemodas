# full_stack_python/articles/detail.py

import reflex as rx 
from ..ui.base import base_page
from . import state

from ..ui.components import not_found_component

# La importación a 'blog.notfound' se ha eliminado para romper el ciclo.
def blog_post_detail_page() -> rx.Component:
    edit_link = rx.link("Editar", href=state.BlogPostState.blog_post_edit_url)
    
    my_child = rx.cond(
        state.BlogPostState.post,
        rx.vstack(
            # ... (todo el vstack del detalle del post no cambia) ...
        ),
        # --- ACTUALIZACIÓN: Usamos el componente compartido ---
        not_found_component(title="Publicación no encontrada")
    )

def article_detail_page() -> rx.Component:
    
    # Se define el componente "no encontrado" aquí mismo para no depender del blog.
    article_not_found = rx.vstack(
        rx.heading("Artículo No Encontrado", size="9"),
        rx.text("El artículo que buscas no existe o no está disponible."),
        spacing="5",
        justify="center",
        align="center",
        min_height="85vh",
    )

    my_child = rx.cond(
        state.ArticlePublicState.post,
        rx.vstack(
            rx.hstack(
                rx.heading(state.ArticlePublicState.post.title, size="9"),
                align='end'
            ),
            rx.text("Por ", state.ArticlePublicState.post.userinfo.user.username),
            rx.cond(
                state.ArticlePublicState.post.publish_date,
                rx.text(state.ArticlePublicState.post.publish_date.to_string()),
            ),
            rx.divider(),
            rx.grid(
                rx.foreach(
                    state.ArticlePublicState.post.images,
                    lambda img: rx.image(
                        src=rx.get_upload_url(img.filename),
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
                state.ArticlePublicState.post.content,
                white_space='pre-wrap'
            ),
            spacing="5",
            align="start",
            min_height="85vh",
        ),
        article_not_found
    )
    return base_page(my_child)