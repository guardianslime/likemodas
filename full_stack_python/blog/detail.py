import reflex as rx 

from ..ui.base import base_page

from . import state
from .notfound import blog_post_not_found
# @rx.page(route="/about")
# full_stack_python/blog/detail.py (CORREGIDO)
def blog_post_detail_page() -> rx.Component:
    con_edit = True
    edit_link = rx.link("Edit", href=f"{state.BlogPostState.blog_post_edit_url}")
    edit_link_el = rx.cond(
        con_edit,
        edit_link,
    )
    # Usamos rx.cond para verificar que 'post' y sus relaciones anidadas existen antes de usarlas
    my_child = rx.cond(
        state.BlogPostState.post,
        rx.vstack(
            rx.hstack(
                rx.heading(state.BlogPostState.post.title, size="9"),
                edit_link_el,
                align='end'
            ),
            # --- INICIO DE LA CORRECCIÓN ---
            rx.cond(
                state.BlogPostState.post.userinfo,
                rx.text(
                    "Autor: ",
                    # Accedemos directamente al atributo 'username' del usuario
                    rx.cond(
                        state.BlogPostState.post.userinfo.user,
                        state.BlogPostState.post.userinfo.user.username,
                        "Usuario Desconocido"
                    ),
                    " (",
                    # Accedemos directamente al atributo 'email'
                    state.BlogPostState.post.userinfo.email,
                    ")"
                ),
                rx.text("Información de usuario no disponible")
            ),
            rx.cond(
                state.BlogPostState.post.publish_date,
                rx.text("Publicado el: ", state.BlogPostState.post.publish_date.to_string()),
                rx.text("Aún no publicado")
            ),
            # --- FIN DE LA CORRECCIÓN ---
            rx.text(
                state.BlogPostState.post.content,
                white_space='pre-wrap'
            ),
            spacing="5",
            align="center",
            min_height="85vh",
        ),
        blog_post_not_found()
    )
    return base_page(my_child)