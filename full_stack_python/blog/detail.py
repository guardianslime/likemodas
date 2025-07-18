# full_stack_python/blog/detail.py

import reflex as rx
from ..ui.base import base_page
from .state import BlogPostState
from .notfound import blog_post_not_found
from ..ui.carousel import carousel

def image_with_expand_button(image_url: str) -> rx.Component:
    """Crea una caja con una imagen y un botón de expandir superpuesto."""
    return rx.box(
        rx.image(
            src=rx.get_upload_url(image_url),
            width="100%",
            height="auto",
            max_height="550px",
            object_fit="contain",
        ),
        rx.icon_button(
            rx.icon(tag="expand"),
            on_click=BlogPostState.open_modal(rx.get_upload_url(image_url)),
            position="absolute",
            top="0.5em",
            right="0.5em",
            variant="soft",
            cursor="pointer",
        ),
        position="relative",
    )

def _image_section() -> rx.Component:
    """Sección para el carrusel de imágenes."""
    return carousel(
        rx.foreach(
            BlogPostState.post.images,
            image_with_expand_button
        ),
        show_indicators=True,
        infinite_loop=True,
        emulate_touch=True,
        show_thumbs=False,
        auto_play=False,
        show_arrows=True,
    )

def _info_section() -> rx.Component:
    """Sección para la información y acciones del post."""
    return rx.vstack(
        rx.text(BlogPostState.post.title, size="7", font_weight="bold", margin_bottom="0.5em", text_align="left"),
        rx.text(BlogPostState.formatted_price, size="6", color="gray", text_align="left"),
        rx.text(BlogPostState.post.content, size="4", margin_top="1em", white_space="pre-wrap", text_align="left"),
        rx.spacer(),
        rx.hstack(
            rx.link(rx.button("Editar Post", variant="soft"), href=BlogPostState.blog_post_edit_url),
            rx.button(
                "Eliminar Post",
                color_scheme="red",
                on_click=BlogPostState.delete_post(BlogPostState.post.id)
            ),
            spacing="4",
            margin_top="2em"
        ),
        padding="1em",
        align="start",
        width="100%",
    )

def blog_post_detail_page() -> rx.Component:
    """Página que muestra el detalle de un post, con un modal para ampliar imágenes."""
    content_grid = rx.cond(
        BlogPostState.post,
        rx.grid(
            _image_section(),
            _info_section(),
            columns={"base": "1", "md": "2"},
            spacing="4",
            align_items="start",
            width="100%",
            max_width="1120px",
        ),
        blog_post_not_found()
    )

    return base_page(
        rx.fragment(
            rx.center(
                rx.vstack(
                    rx.heading("Detalle de mi Publicación", size="8", margin_bottom="1em"),
                    content_grid,
                    spacing="6",
                    width="100%",
                    padding="2em",
                    align="center",
                ),
                width="100%",
            ),
            # ✨ CORRECCIÓN FINAL: Usamos rx.radix.themes.dialog en lugar de rx.modal
            rx.radix.themes.dialog.root(
                rx.radix.themes.dialog.content(
                    style={"max_width": "80vw", "max_height": "90vh"},
                    rx.radix.themes.dialog.body(
                        rx.image(src=BlogPostState.modal_image_src, width="100%", height="auto")
                    ),
                    rx.radix.themes.dialog.close(
                        rx.icon_button(rx.icon(tag="x"), variant="soft", size="2", position="absolute", top="0.5em", right="0.5em")
                    ),
                ),
                open=BlogPostState.show_modal,
                on_open_change=BlogPostState.close_modal, # Permite cerrar haciendo clic fuera
            )
        )
    )
