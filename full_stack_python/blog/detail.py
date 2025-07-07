# full_stack_python/blog/detail.py

import reflex as rx 
from ..ui.base import base_page
from . import state
from .notfound import blog_post_not_found

def post_image_gallery_item(image: state.PostImageModel) -> rx.Component:
    """Muestra una imagen de la galería del post."""
    return rx.image(
        src=rx.get_upload_url(image.img_name),
        width="100%",
        height="auto",
        border_radius="0.5em"
    )

def blog_post_detail_page() -> rx.Component:
    post_is_loaded = (state.BlogPostState.post) & (state.BlogPostState.post.userinfo) & (state.BlogPostState.post.userinfo.user)

    my_child = rx.cond(
        post_is_loaded,
        rx.vstack(
            # Título y botón de editar
            rx.hstack(
                rx.heading(state.BlogPostState.post.title, size="9"),
                rx.link(
                    rx.button("Editar Post"),
                    href=state.BlogPostState.blog_post_edit_url
                ),
                align='center',
                justify='between',
                width="100%"
            ),
            
            # Información del autor y fecha
            rx.hstack(
                rx.text("Publicado por: ", rx.code(state.BlogPostState.post.userinfo.user.username)),
                rx.spacer(),
                rx.text(f"Última actualización: {state.BlogPostState.post.updated_at.to_string()}"),
                width="100%",
                color_scheme="gray"
            ),
            
            rx.divider(width="100%"),
            
            # Contenido de texto
            rx.text(
                state.BlogPostState.post.content,
                white_space='pre-wrap'
            ),
            
            # Galería de imágenes
            rx.heading("Imágenes", size="6", margin_top="1.5em"),
            rx.grid(
                rx.foreach(
                    state.BlogPostState.post.images,
                    post_image_gallery_item
                ),
                columns=["1", "2", "3"],
                spacing="4",
                width="100%"
            ),
            
            spacing="5",
            align="start",
            min_height="85vh",
            width="100%",
            max_width="900px",
            margin="auto"
        ),
        blog_post_not_found()
    )
    
    return base_page(my_child)