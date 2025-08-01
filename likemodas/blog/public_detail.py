# likemodas/blog/public_detail.py (CORREGIDO)

import reflex as rx
import math

from .state import CommentState
from ..auth.state import SessionState
from ..cart.state import CartState
from ..models import CommentModel
from ..ui.base import base_page
from ..ui.carousel import Carousel
from ..ui.skeletons import skeleton_product_detail_view

# --- (Aquí irían tus funciones de UI como _image_section, _info_section, etc. No necesitan cambios) ---
def _image_section() -> rx.Component:
    return rx.box(
        Carousel.create(
            rx.foreach(
                CommentState.post.image_urls,
                lambda image_url: rx.image(
                    src=rx.get_upload_url(image_url),
                    alt=CommentState.post.title,
                    width="100%",
                    height="auto",
                    object_fit="cover",
                    border_radius="var(--radius-3)",
                )
            ),
            show_arrows=True, show_indicators=True, infinite_loop=True, auto_play=True, width="100%"
        ),
        width="100%", max_width="800px", margin="auto", padding_y="1em"
    )

def _info_section() -> rx.Component:
    # ... (código de tu sección de información)
    return rx.vstack(
        rx.text(CommentState.post.title, size="9", font_weight="bold"),
        rx.text(CommentState.formatted_price, size="7", color="gray"),
        rx.button(
            "Añadir al Carrito",
            on_click=CartState.add_to_cart(CommentState.post.id),
            width="100%", size="4", margin_top="1.5em", color_scheme="violet"
        ),
        padding="1em", align="start", width="100%",
    )

def comment_section() -> rx.Component:
    # ... (código de tu sección de comentarios)
    return rx.vstack(rx.heading("Opiniones"))


# --- ✅ SOLUCIÓN AL "Page redefined" ---
# Se elimina el decorador `@rx.page(...)` de aquí.
# La definición de la ruta se deja únicamente en el archivo principal `likemodas/likemodas.py`,
# lo que elimina la advertencia y previene conflictos.
def blog_public_detail_page() -> rx.Component:
    return rx.cond(
        SessionState.is_hydrated,
        base_page(
            rx.cond(
                CommentState.is_loading,
                skeleton_product_detail_view(),
                rx.vstack(
                    rx.heading("Detalle del Producto", size="9", margin_bottom="1em"),
                    rx.cond(
                        CommentState.post,
                        rx.vstack(
                            rx.grid(
                                _image_section(),
                                _info_section(),
                                columns={"base": "1", "md": "2"},
                                spacing="4",
                                align_items="start",
                                width="100%",
                                max_width="1400px",
                            ),
                            comment_section(),
                            spacing="6",
                            width="100%",
                            align="center",
                        ),
                        rx.center(rx.text("Publicación no encontrada o no disponible.", color="red", size="5"), height="50vh")
                    ),
                    width="100%",
                    padding="2em",
                )
            )
        ),
        rx.center(rx.spinner(), height="100vh")
    )