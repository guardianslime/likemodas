# likemodas/blog/public_detail.py (VERSIÓN FINAL Y CORREGIDA)

import reflex as rx
from ..state import AppState
from ..ui.carousel import Carousel
from ..models import CommentModel
from ..ui.skeletons import skeleton_product_detail_view

def _image_section() -> rx.Component:
    """Muestra el carrusel de imágenes del producto."""
    return rx.box(
        Carousel.create(
            rx.foreach(
                AppState.post.image_urls,
                lambda image_url: rx.image(
                    src=rx.get_upload_url(image_url), alt=AppState.post.title,
                    width="100%", height="auto", object_fit="cover", border_radius="var(--radius-3)",
                )
            ),
            show_arrows=True, show_indicators=True, infinite_loop=True,
            auto_play=True, width="100%"
        ),
        width="100%", max_width="800px", margin="auto", padding_y="1em"
    )

def _info_section() -> rx.Component:
    """Muestra la información de texto y el botón de compra del producto."""
    return rx.vstack(
        rx.vstack(
            rx.text(AppState.post.title, size="9", font_weight="bold", margin_bottom="0.25em", text_align="left"),
            rx.text("Publicado el " + AppState.post.created_at_formatted, size="3", color_scheme="gray", margin_bottom="0.5em", text_align="left", width="100%"),
            rx.text(AppState.post.price_cop, size="7", color="gray", text_align="left"),
            rx.text(AppState.post.content, size="5", margin_top="1em", white_space="pre-wrap", text_align="left"),
            align="start",
            spacing="2",
        ),
        rx.button(
            "Añadir al Carrito",
            on_click=lambda: AppState.add_to_cart(AppState.post.id),
            width="100%", size="4", margin_top="1.5em", color_scheme="violet"
        ),
        justify_content="space-between",
        padding="1em",
        align_items="stretch",
        width="100%",
        min_height="350px",
    )

def blog_public_detail_content() -> rx.Component:
    """
    Página de detalle del producto con una guardia de carga robusta
    que elimina la condición de carrera y el parpadeo.
    """
    return rx.center(
        rx.vstack(
            # --- ✅ LÓGICA DE RENDERIZADO A PRUEBA DE FALLOS ---
            rx.cond(
                AppState.is_post_loading,
                # ESTADO 1: Muestra el esqueleto MIENTRAS la carga está en progreso.
                skeleton_product_detail_view(),
                
                # Una vez que la carga TERMINA, decide qué mostrar.
                rx.cond(
                    AppState.post,
                    # ESTADO 3: Si el post EXISTE, muestra el contenido real.
                    rx.fragment(
                        rx.heading("Detalle del Producto", size="9", margin_bottom="1em", color_scheme="violet"),
                        rx.grid(
                            _image_section(), _info_section(),
                            columns="2", spacing="4", align_items="start",
                            width="100%", max_width="1400px",
                        ),
                    ),
                    # ESTADO 2: Si la carga terminó y el post NO EXISTE, muestra un error permanente.
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