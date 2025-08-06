# likemodas/blog/public_detail.py (VERSIÓN FINAL Y ROBUSTA)

import reflex as rx
from ..state import AppState
from ..ui.carousel import Carousel
from ..models import CommentModel
from ..ui.skeletons import skeleton_product_detail_view

# --- ▼▼▼ CAMBIO CRÍTICO AQUÍ ▼▼▼ ---

def _image_section() -> rx.Component:
    """
    Muestra el carrusel o un placeholder, ambos forzados a tener una altura fija
    para eliminar el salto de diseño (layout shift).
    """
    # Define una altura fija y consistente para el contenedor de la imagen.
    # Puedes ajustar este valor (ej. "450px", "60vh", etc.) según tu diseño.
    FIXED_HEIGHT = "500px"

    # El carrusel real, ahora con una altura fija.
    carousel_component = Carousel.create(
        rx.foreach(
            AppState.post.image_urls,
            lambda image_url: rx.image(
                src=rx.get_upload_url(image_url),
                alt=AppState.post.title,
                width="100%",
                height="100%", # Ocupa el 100% de la altura del contenedor
                object_fit="cover",
            )
        ),
        show_arrows=True, show_indicators=True, infinite_loop=True,
        auto_play=True, width="100%",
        # La altura se aplica al contenedor del carrusel.
        height=FIXED_HEIGHT,
        border_radius="var(--radius-3)",
    )

    # El marcador de posición (placeholder), con EXACTAMENTE la misma altura fija.
    placeholder_component = rx.box(
        rx.vstack(
            rx.icon("image_off", size=48, color=rx.color("gray", 8)),
            rx.text("Sin imagen disponible"),
            align="center", justify="center"
        ),
        width="100%",
        height=FIXED_HEIGHT,
        bg=rx.color("gray", 3),
        border_radius="var(--radius-3)",
        display="flex",
    )

    return rx.box(
        rx.cond(
            AppState.post & AppState.post.image_urls,
            carousel_component,
            placeholder_component
        ),
        width="100%", max_width="800px", margin="auto", padding_y="1em"
    )

# --- El resto del archivo permanece igual ---

def _info_section() -> rx.Component:
    """Muestra la información de texto y el botón de compra del producto."""
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
    """Página de detalle con la lógica de carga y renderizado final."""
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