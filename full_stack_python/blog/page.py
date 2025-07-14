# full_stack_python/blog/page.py (CORREGIDO)

import reflex as rx
from ..ui.base import base_page 
from full_stack_python.blog.state import BlogPublicState
from full_stack_python.navigation import routes

def blog_public_page():
    """Página pública que muestra la galería de productos con un layout responsivo único."""

    my_child = rx.center(
        rx.vstack(
            rx.heading("Publicaciones", size="6"),
            
            # --- ✨ CORRECCIÓN AQUÍ ✨ ---
            # Se usa un único rx.grid con columnas responsivas para todos los tamaños de pantalla.
            rx.grid(
                rx.foreach(
                    BlogPublicState.posts,
                    lambda post: rx.box(
                        rx.link(
                            rx.vstack(
                                rx.box(
                                    rx.cond(
                                        post.images & (post.images.length() > 0),
                                        rx.image(
                                            src=rx.get_upload_url(post.images[0]),
                                            width="100%",
                                            height="100%",
                                            object_fit="cover",
                                            border_radius="md",
                                            style={
                                                "transition": "transform 0.3s ease-in-out",
                                                "_hover": {
                                                    "transform": "scale(1.05)"
                                                }
                                            }
                                        ),
                                        rx.box(
                                            "Sin imagen",
                                            width="100%",
                                            height="100%",
                                            bg="#eee",
                                            align="center",
                                            justify="center",
                                            display="flex",
                                            border_radius="md"
                                        )
                                    ),
                                    position="relative",
                                    width="260px",
                                    height="260px"
                                ),
                                rx.text(
                                    post.title,
                                    weight="bold",
                                    size="6",
                                    padding_left="3px",
                                    white_space="normal",
                                    word_break="break-word",
                                    color=rx.color_mode_cond("black", "white"),
                                ),
                                rx.text(
                                    rx.cond(
                                        post.price,
                                        "$" + post.price.to(str),
                                        "$0.00"
                                    ),
                                    color=rx.color_mode_cond("black", "white"),
                                    size="6",
                                    padding_left="3px",
                                    white_space="normal",
                                    word_break="break-word"
                                ),
                                spacing="2",
                                align="start"
                            ),
                            href=f"{routes.BLOG_PUBLIC_DETAIL_ROUTE}/{post.id}"
                        ),
                        bg=rx.color_mode_cond("#f9f9f9", "#111111"),
                        border=rx.color_mode_cond("1px solid #e5e5e5", "1px solid #1a1a1a"),
                        border_radius="8px",
                        box_shadow="md",
                        min_height="380px"
                    )
                ),
                # Columnas responsivas: 2 para móvil, 3 para tablet, 6 para desktop.
                columns=["2", "3", "6"], 
                spacing="6",
                width="100%",
                max_width="11200px",
                justify_content="center"
            ),
            spacing="6",
            width="100%",
            padding="2em",
            align="center"
        ),
        width="100%"
    )
    
    return base_page(my_child)