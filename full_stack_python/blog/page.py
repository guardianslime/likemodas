# full_stack_python/blog/page.py (CORREGIDO Y COMPLETO)

import reflex as rx
from ..ui.base import base_page 
# --- ✨ CAMBIO: Se importa el estado del carrito en lugar del estado público del blog ---
from ..cart.state import CartState 
from ..navigation import routes

def blog_public_page():
    """
    Página pública que muestra la galería de productos, ahora con la funcionalidad
    para añadir productos al carrito de compras.
    """

    my_child = rx.center(
        rx.vstack(
            rx.heading("Publicaciones", size="6"),
            
            rx.grid(
                # --- ✨ CAMBIO: Se itera sobre los posts desde CartState ---
                rx.foreach(
                    CartState.posts,
                    lambda post: rx.box(
                        rx.vstack(
                            # El link ahora envuelve solo la imagen y el texto descriptivo
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
                            # --- ✨ NUEVO: Botón para añadir al carrito ---
                            rx.button(
                                "Añadir al Carrito",
                                on_click=CartState.add_to_cart(post.id),
                                width="100%",
                                margin_top="0.5em"
                            ),
                            align="start",
                            spacing="2"
                        ),
                        bg=rx.color_mode_cond("#f9f9f9", "#111111"),
                        border=rx.color_mode_cond("1px solid #e5e5e5", "1px solid #1a1a1a"),
                        border_radius="8px",
                        box_shadow="md",
                        padding="1em", # Se añade padding para que el botón no quede pegado al borde
                        min_height="380px"
                    )
                ),
                # Se mantiene la estructura de columnas responsivas
                columns={
                    "base": "2",
                    "md": "3",
                    "lg": "6",
                },
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