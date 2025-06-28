import reflex as rx 
from ..ui.base import base_page
from . import state
from .notfound import blog_post_not_found

def blog_post_detail_page() -> rx.Component:
    """
    Página de detalle del post, ahora con verificaciones para evitar errores de renderizado.
    """
    
    # --- INICIO DE LA CORRECCIÓN ---
    # Creamos una variable segura para mostrar el nombre del autor.
    # Usamos rx.cond para asegurarnos de que no falle si los datos anidados no han cargado.
    author_display = rx.cond(
        state.BlogPostState.post.userinfo,
        rx.cond(
            state.BlogPostState.post.userinfo.user,
            rx.text("Autor: ", state.BlogPostState.post.userinfo.user.username, weight="bold"),
            rx.text("Autor no disponible")
        ),
        rx.text("Cargando autor...")
    )
    # --- FIN DE LA CORRECCIÓN ---

    my_child = rx.cond(
        state.BlogPostState.post,
        rx.vstack(
            rx.hstack(
                rx.heading(state.BlogPostState.post.title, size="9"),
                rx.link("Editar", href=state.BlogPostState.blog_post_edit_url, button=True, variant="outline"),
                align='end',
                justify='between',
                width="100%"
            ),
            
            author_display,  # Usamos la variable segura que creamos arriba
            
            rx.text(f"Publicado: {state.BlogPostState.post.publish_date}"),
            rx.divider(),
            rx.markdown(
                state.BlogPostState.post.content,
                padding="1em",
            ),
            spacing="5",
            align_items="start", # Alineamos al inicio para una mejor lectura
            min_height="85vh",
            width="100%",
            max_width="960px",
            margin="auto",
            padding_y="2em"
        ),
        blog_post_not_found()
    )
    return base_page(my_child)