# likemodas/blog/page.py (CORREGIDO)

import reflex as rx
from ..ui.base import base_page 
from ..cart.state import CartState 
from ..navigation import routes

def blog_public_page():
    """
    Página pública que muestra la galería de productos con espaciado flexible y adaptable.
    """
    my_child = rx.center(
        rx.vstack(
            rx.heading("Publicaciones", size="6"),
            
            # --- ✨ CAMBIO CLAVE: Se usa rx.flex en lugar de rx.grid ✨ ---
            rx.flex(
                rx.foreach(
                    CartState.posts,
                    lambda post: rx.box(
                        # La definición de la tarjeta con tamaño fijo no cambia
                        rx.vstack(
                            rx.link(
                                rx.vstack(
                                    rx.box(
                                        rx.cond(
                                            post.images & (post.images.length() > 0),
                                            rx.image(
                                                src=rx.get_upload_url(post.images[0]),
                                                width="100%", height="100%", object_fit="cover", border_radius="md",
                                            ),
                                            rx.box(
                                                "Sin imagen", width="100%", height="100%", bg="#eee",
                                                align="center", justify="center", display="flex", border_radius="md"
                                            )
                                        ),
                                        position="relative", width="260px", height="260px"
                                    ),
                                    rx.text(post.title, weight="bold", size="6", color=rx.color_mode_cond("black", "white")),
                                    rx.text(rx.cond(post.price, "$" + post.price.to(str), "$0.00"), color=rx.color_mode_cond("black", "white"), size="6"),
                                    spacing="2", align="start"
                                ),
                                href=f"{routes.BLOG_PUBLIC_DETAIL_ROUTE}/{post.id}"
                            ),
                            rx.spacer(),
                            rx.button(
                                "Añadir al Carrito",
                                on_click=lambda: CartState.add_to_cart(post.id),
                                width="100%",
                            ),
                            align="center", spacing="2", height="100%"
                        ),
                        width="290px", height="420px",
                        bg=rx.color_mode_cond("#f9f9f9", "#111111"),
                        border=rx.color_mode_cond("1px solid #e5e5e5", "1px solid #1a1a1a"),
                        border_radius="8px",
                        box_shadow="md",
                        padding="1em",
                    )
                ),
                # Propiedades de rx.flex para el diseño adaptable
                wrap="wrap",        # Permite que las tarjetas pasen a la siguiente línea.
                spacing="6",        # Define el espacio entre las tarjetas.
                justify="center",   # Centra las tarjetas en el contenedor.
                width="100%",
                max_width="1800px", # Un ancho máximo generoso para pantallas grandes.
            ),
            spacing="6",
            width="100%",
            padding="2em",
            align="center"
        ),
        width="100%"
    )
    
    return base_page(my_child)