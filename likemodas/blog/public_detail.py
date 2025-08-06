# likemodas/blog/public_detail.py (VERSIÓN CON CARRUSEL NATIVO)

import reflex as rx
from ..state import AppState
from ..models import CommentModel
from ..ui.skeletons import skeleton_product_detail_view

def _image_section() -> rx.Component:
    """
    Un carrusel de imágenes nativo y simple construido con componentes de Reflex,
    eliminando la librería externa y los errores de hidratación.
    """
    FIXED_HEIGHT = "500px"

    # --- ✅ NUESTRO CARRUSEL NATIVO ---
    native_carousel = rx.box(
        # La imagen principal, su 'src' ahora depende del estado del índice.
        rx.image(
            src=rx.get_upload_url(AppState.current_image_url),
            alt=AppState.post.title,
            width="100%",
            height="100%",
            object_fit="cover",
        ),
        # Botón de control "Anterior"
        rx.button(
            rx.icon(tag="chevron-left"),
            on_click=AppState.prev_image,
            position="absolute",
            top="50%",
            left="0.5rem",
            transform="translateY(-50%)",
            variant="soft",
            color_scheme="gray",
        ),
        # Botón de control "Siguiente"
        rx.button(
            rx.icon(tag="chevron-right"),
            on_click=AppState.next_image,
            position="absolute",
            top="50%",
            right="0.5rem",
            transform="translateY(-50%)",
            variant="soft",
            color_scheme="gray",
        ),
        position="relative",
        width="100%",
        height=FIXED_HEIGHT,
        border_radius="var(--radius-3)",
        overflow="hidden", # Esconde cualquier desbordamiento de la imagen
    )

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
            native_carousel,
            placeholder_component
        ),
        width="100%", max_width="800px", margin="auto", padding_y="1em"
    )

# --- El resto del archivo permanece sin cambios ---

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