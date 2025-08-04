# likemodas/blog/public_detail.py

import reflex as rx
import math

# --- CORRECCIÓN CLAVE ---
# Se eliminó 'from likemodas.state import AppState'.
# En su lugar, importamos los estados específicos que esta página necesita.
from ..auth.state import SessionState
from ..cart.state import CartState
from .state import CommentState

from ..ui.carousel import Carousel
from ..models import CommentModel

def _image_section() -> rx.Component:
    """Muestra las imágenes del post en un carrusel."""
    return rx.box(
        Carousel.create(
            rx.foreach(
                # Se usa CommentState en lugar de AppState.comments
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
            show_arrows=True,
            show_indicators=True,
            infinite_loop=True,
            auto_play=True,
            width="100%"
        ),
        width="100%",
        max_width="800px",
        margin="auto",
        padding_y="1em"
    )

def _info_section() -> rx.Component:
    """Muestra la información principal del producto."""
    return rx.vstack(
        rx.text(CommentState.post.title, size="9", font_weight="bold", margin_bottom="0.25em", text_align="left"),
        rx.text("Publicado el " + CommentState.post.created_at_formatted, size="3", color_scheme="gray", margin_bottom="0.5em", text_align="left", width="100%"),
        rx.text(CommentState.formatted_price, size="7", color="gray", text_align="left"),
        rx.text(CommentState.content, size="5", margin_top="1em", white_space="pre-wrap", text_align="left"),
        rx.spacer(),
        rx.button(
            "Añadir al Carrito",
            # Se usa CartState en lugar de AppState.cart
            on_click=lambda: CartState.add_to_cart(CommentState.post.id),
            width="100%", size="4", margin_top="1.5em", color_scheme="violet"
        ),
        padding="1em",
        align="start",
        width="100%",
        min_height="350px",
    )

def _star_rating_input() -> rx.Component:
    """Componente para que el usuario seleccione una calificación."""
    return rx.hstack(
        rx.foreach(
            rx.Var.range(5),
            lambda i: rx.icon(
                tag="star",
                color=rx.cond(i < CommentState.new_comment_rating, "gold", rx.color("gray", 8)),
                on_click=lambda: CommentState.set_new_comment_rating(i + 1),
                cursor="pointer",
                size=32,
            )
        ),
        spacing="2",
        padding_y="0.5em",
    )

def _comment_form() -> rx.Component:
    """Formulario para añadir un nuevo comentario."""
    return rx.cond(
        # Se usa SessionState para la comprobación de autenticación
        SessionState.is_authenticated,
        rx.cond(
            CommentState.user_can_comment,
            rx.form(
                rx.vstack(
                    rx.text("Tu calificación:", weight="bold", size="4"),
                    _star_rating_input(),
                    rx.text_area(name="comment_text", value=CommentState.new_comment_text, on_change=CommentState.set_new_comment_text, placeholder="Escribe tu opinión...", width="100%", size="3"),
                    rx.button("Publicar Opinión", type="submit", align_self="flex-end", size="3", color_scheme="violet"),
                    spacing="3", width="100%",
                ),
                on_submit=CommentState.add_comment, width="100%",
            ),
            rx.box(
                rx.cond(
                    CommentState.user_has_commented,
                    rx.text("Ya has publicado una opinión para este producto.", size="4"),
                    rx.text("Debes haber comprado este producto para poder dejar tu opinión.", size="4")
                ),
                padding="1.5em", border="1px solid #444", border_radius="md", text_align="center", width="100%",
            )
        ),
        rx.box(
            rx.text("Debes ", rx.link("iniciar sesión", href="/login"), " y comprar este producto para poder comentarlo.", size="4"),
            padding="1.5em", border="1px solid #444", border_radius="md", text_align="center", width="100%",
        )
    )

def comment_section() -> rx.Component:
    """Sección completa de comentarios."""
    return rx.vstack(
        rx.divider(margin_y="2em"),
        rx.heading("Opiniones del Producto", size="8", color_scheme="violet"),
        _comment_form(),
        rx.vstack(
            rx.foreach(CommentState.comments, lambda comment: rx.box(rx.text(comment.content))), # Simplificado para el ejemplo
            spacing="4", width="100%", margin_top="1.5em",
        ),
        spacing="5", width="100%", max_width="1120px", align="center", padding_top="1em",
    )

def blog_public_detail_content() -> rx.Component:
    """Página que muestra el detalle de una publicación pública."""
    return rx.center(
        rx.vstack(
            rx.heading("Detalle del Producto", size="9", margin_bottom="1em", color_scheme="violet"),
            rx.cond(
                CommentState.post,
                rx.fragment(
                    rx.grid(
                        _image_section(),
                        _info_section(),
                        columns="2",
                        spacing="4",
                        align_items="start",
                        width="100%",
                        max_width="1400px",
                    ),
                    comment_section(),
                ),
                rx.center(
                    rx.cond(
                        SessionState.is_hydrated,
                        rx.text("Publicación no encontrada o no disponible.", color="red"),
                        rx.spinner(size="3")
                    ),
                    min_height="50vh"
                )
            ),
            spacing="6",
            width="100%",
            padding="2em",
            align="center",
        ),
        width="100%",
    )