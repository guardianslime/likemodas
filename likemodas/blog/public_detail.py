# likemodas/blog/public_detail.py (CORREGIDO)

import reflex as rx
from ..state import AppState
from ..ui.carousel import Carousel
from ..models import CommentModel
from ..ui.skeletons import skeleton_product_detail_view # Importa el esqueleto

def _image_section() -> rx.Component:
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
    return rx.vstack(
        # Se agrupa todo el contenido superior en un vstack propio.
        rx.vstack(
            rx.text(AppState.post.title, size="9", font_weight="bold", margin_bottom="0.25em", text_align="left"),
            rx.text("Publicado el " + AppState.post.created_at_formatted, size="3", color_scheme="gray", margin_bottom="0.5em", text_align="left", width="100%"),
            rx.text(AppState.post.price_cop, size="7", color="gray", text_align="left"),
            rx.text(AppState.post.content, size="5", margin_top="1em", white_space="pre-wrap", text_align="left"),
            align="start",
            spacing="2", # Ajusta el espaciado si es necesario
        ),
        
        # El botón ahora es un hijo directo del vstack principal.
        rx.button(
            "Añadir al Carrito",
            on_click=lambda: AppState.add_to_cart(AppState.post.id),
            width="100%", size="4", margin_top="1.5em", color_scheme="violet"
        ),
        
        # --- CAMBIOS CLAVE ---
        # 1. Se elimina el `rx.spacer()`.
        # 2. Se usa `justify_content` para empujar el botón hacia abajo.
        justify_content="space-between",
        
        padding="1em", 
        align_items="stretch", # Asegura que los hijos ocupen el ancho.
        width="100%", 
        min_height="350px",
    )

def blog_public_detail_content() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading("Detalle del Producto", size="9", margin_bottom="1em", color_scheme="violet"),
            # ✅ CORRECCIÓN: Patrón de estado de carga completo
            rx.cond(
                AppState.is_hydrated,
                rx.cond(
                    AppState.post,
                    # Si el post existe, muestra los detalles
                    rx.fragment(
                        rx.grid(
                            _image_section(), _info_section(),
                            columns="2", spacing="4", align_items="start",
                            width="100%", max_width="1400px",
                        ),
                        # comment_section(), # Puedes añadir esta sección después
                    ),
                    # Si el post no existe (después de cargar), muestra mensaje de no encontrado
                    rx.center(
                        rx.text("Publicación no encontrada o no disponible.", color="red"),
                        min_height="50vh"
                    )
                ),
                # Muestra un esqueleto o spinner mientras los datos se cargan
                skeleton_product_detail_view()
            ),
            spacing="6", width="100%", padding="2em", align="center",
        ),
        width="100%",
    )