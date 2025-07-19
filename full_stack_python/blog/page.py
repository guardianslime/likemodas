# full_stack_python/blog/page.py (CORREGIDO Y COMPLETO)

import reflex as rx
from ..ui.base import base_page 
from ..cart.state import CartState 
from ..navigation import routes

def blog_public_page():
    """
    Página pública que muestra la galería de productos con tarjetas de tamaño fijo.
    """
    my_child = rx.center(
        rx.vstack(
            rx.heading("Publicaciones", size="6"),
            
            rx.grid(
                rx.foreach(
                    CartState.posts,
                    lambda post: rx.box(
                        # Contenedor principal de la tarjeta
                        rx.vstack(
                            # Contenido superior (imagen y texto) que lleva al detalle
                            rx.link(
                                rx.vstack(
                                    # Contenedor de la imagen (mantiene su tamaño fijo)
                                    rx.box(
                                        rx.cond(
                                            post.images & (post.images.length() > 0),
                                            rx.image(
                                                src=rx.get_upload_url(post.images[0]),
                                                width="100%",
                                                height="100%",
                                                object_fit="cover",
                                                border_radius="md",
                                            ),
                                            rx.box(
                                                "Sin imagen", width="100%", height="100%", bg="#eee",
                                                align="center", justify="center", display="flex",
                                                border_radius="md"
                                            )
                                        ),
                                        position="relative",
                                        width="260px",
                                        height="260px"
                                    ),
                                    # Título y precio
                                    rx.text(
                                        post.title, weight="bold", size="6",
                                        color=rx.color_mode_cond("black", "white"),
                                    ),
                                    rx.text(
                                        rx.cond(post.price, "$" + post.price.to(str), "$0.00"),
                                        color=rx.color_mode_cond("black", "white"), size="6",
                                    ),
                                    spacing="2", align="start"
                                ),
                                href=f"{routes.BLOG_PUBLIC_DETAIL_ROUTE}/{post.id}"
                            ),
                            # Espaciador para empujar el botón hacia abajo
                            rx.spacer(),
                            # Botón de añadir al carrito
                            rx.button(
                                "Añadir al Carrito",
                                on_click=lambda: CartState.add_to_cart(post.id),
                                width="100%",
                            ),
                            # Alineación y espaciado del contenido interno de la tarjeta
                            align="center",
                            spacing="2",
                            height="100%" # Asegura que el vstack use toda la altura de la tarjeta
                        ),
                        
                        # --- ✨ CAMBIOS CLAVE AQUÍ ✨ ---
                        # Se establece un tamaño fijo para la tarjeta.
                        width="290px",
                        height="420px",
                        
                        # Estilos visuales de la tarjeta
                        bg=rx.color_mode_cond("#f9f9f9", "#111111"),
                        border=rx.color_mode_cond("1px solid #e5e5e5", "1px solid #1a1a1a"),
                        border_radius="8px",
                        box_shadow="md",
                        padding="1em",
                    )
                ),
                # La configuración del grid se mantiene para la responsividad
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