# likemodas/blog/public_detail.py (VERSIÓN CON LA SOLUCIÓN 'key')

import reflex as rx
from ..state import AppState
from ..ui.carousel import Carousel
from ..models import CommentModel
from ..ui.skeletons import skeleton_product_detail_view

def _image_section() -> rx.Component:
    """
    Muestra el carrusel o un placeholder, usando una 'key' dinámica para
    forzar un re-montaje limpio y eliminar errores de inicialización.
    """
    FIXED_HEIGHT = "500px"

    placeholder_component = rx.box(
        rx.vstack(
            rx.icon("image_off", size=48, color=rx.color("gray", 8)),
            rx.text("Sin imagen disponible"),
            align="center", justify="center"
        ),
        width="100%", height=FIXED_HEIGHT, bg=rx.color("gray", 3),
        border_radius="var(--radius-3)", display="flex",
    )

    return rx.box(
        rx.cond(
            AppState.post & AppState.post.image_urls,
            # --- ▼▼▼ LA CORRECCIÓN DEFINITIVA ESTÁ AQUÍ ▼▼▼ ---
            # Al añadir una 'key' única, forzamos a Reflex/React a destruir
            # cualquier instancia anterior del carrusel y crear una NUEVA desde cero
            # solo cuando los datos están listos. Esto limpia cualquier estado
            # de inicialización corrupto que causaba los errores de la consola.
            Carousel.create(
                rx.foreach(
                    AppState.post.image_urls,
                    lambda image_url: rx.image(
                        src=rx.get_upload_url(image_url),
                        alt=AppState.post.title,
                        width="100%",
                        height="100%",
                        object_fit="cover",
                    )
                ),
                key=AppState.post.id,  # <-- LA CLAVE DEL ARREGLO
                show_arrows=True, show_indicators=True, infinite_loop=True,
                auto_play=True, width="100%", height=FIXED_HEIGHT,
                border_radius="var(--radius-3)",
            ),
            placeholder_component
        ),
        width="100%", max_width="800px", margin="auto", padding_y="1em"
    )

# --- El resto del archivo permanece exactamente igual ---

def _info_section() -> rx.Component:
    # (Sin cambios en esta función)
    return rx.vstack(
        rx.vstack(
            rx.text(AppState.post.title, size="9", font_weight="bold", margin_bottom="0.25em", text_align="left"),
            rx.text("Publicado el " + AppState.post.created_at_formatted, size="3", color_scheme="gray", margin_bottom="0.5em", text_align="left", width="100%"),
            rx.text(AppState.post.price_cop, size="7", color="gray", text_align="left"),
            rx.text(AppState.post.content, size="5", margin_top="1em", white_space="pre-wrap", text_align="left"),
            align="start", spacing="2",
        ),
        rx.button(
            "Añadir al Carrito",
            on_click=lambda: AppState.add_to_cart(AppState.post.id),
            width="100%", size="4", margin_top="1.5em", color_scheme="violet"
        ),
        justify_content="space-between", padding="1em", align_items="stretch",
        width="100%", min_height="350px",
    )

def blog_public_detail_content() -> rx.Component:
    # (Sin cambios en esta función)
    return rx.center(
        rx.vstack(
            rx.cond(
                AppState.is_post_loading,
                skeleton_product_detail_view(),
                rx.cond(
                    AppState.post,
                    rx.fragment(
                        rx.heading("Detalle del Producto", size="9", margin_bottom="1em", color_scheme="violet"),
                        rx.grid(
                            _image_section(), _info_section(),
                            columns="2", spacing="4", align_items="start",
                            width="100%", max_width="1400px",
                        ),
                    ),
                    rx.center(
                        rx.text("Publicación no encontrada o no disponible.", color="red"),
                        min_height="50vh"
                    )
                )
            ),
            spacing="6", width="100%", padding="2em", align="center",
        ),
        width="100%",
    )