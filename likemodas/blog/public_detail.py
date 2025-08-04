# likemodas/blog/public_detail.py (CORREGIDO)

import reflex as rx
import math

# ✨ 1. Se importa el estado global y unificado
from likemodas.state import AppState

from ..ui.carousel import Carousel
from ..models import CommentModel
from ..ui.base import base_page

# ✨ 2. Todas las llamadas a estados específicos (CommentState, CartState, SessionState)
#    se reemplazan por AppState y su sub-estado correspondiente (comments, cart, etc.)

def _image_section() -> rx.Component:
    """Muestra las imágenes del post en un carrusel."""
    return rx.box(
        Carousel.create(
            rx.foreach(
                AppState.comments.post.image_urls,
                lambda image_url: rx.image(
                    src=rx.get_upload_url(image_url),
                    alt=AppState.comments.post.title,
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

def _global_rating_display() -> rx.Component:
    """Muestra la calificación promedio del producto."""
    average_rating = AppState.comments.average_rating
    rating_count = AppState.comments.rating_count
    full_stars = rx.Var.range(math.floor(average_rating))
    has_half_star = (average_rating - math.floor(average_rating)) >= 0.5
    empty_stars = rx.Var.range(5 - math.ceil(average_rating))

    return rx.cond(
        rating_count > 0,
        rx.hstack(
            rx.foreach(full_stars, lambda _: rx.icon("star", color="gold", size=30)),
            rx.cond(has_half_star, rx.icon("star_half", color="gold", size=30), rx.fragment()),
            rx.foreach(empty_stars, lambda _: rx.icon("star", color=rx.color("gray", 8), size=30)),
            rx.text(f"{average_rating:.1f} de 5", size="4", weight="bold", margin_left="0.5em"),
            rx.text(f"({rating_count} opiniones)", size="4", color_scheme="gray"),
            align="center", spacing="1", padding_y="1em"
        ),
        rx.box(
            rx.text("Este producto aún no tiene calificaciones.", color_scheme="gray", size="4"),
            padding_y="1em"
        )
    )

def _attributes_display() -> rx.Component:
    """Muestra las características (atributos) del producto."""
    return rx.cond(
        AppState.comments.product_attributes,
        rx.vstack(
            rx.divider(margin_y="1em"),
            rx.heading("Características", size="5", width="100%", text_align="left", margin_bottom="0.5em"),
            rx.vstack(
                rx.foreach(
                    AppState.comments.product_attributes,
                    lambda attr: rx.hstack(
                        rx.text(attr[0], weight="bold", min_width="160px"),
                        rx.text(attr[1]),
                        spacing="4",
                        width="100%",
                    )
                ),
                spacing="2", align_items="start", padding_y="0.5em"
            ),
            align_items="start", width="100%",
        )
    )

def _info_section() -> rx.Component:
    """Muestra la información principal del producto."""
    return rx.vstack(
        rx.text(AppState.comments.post.title, size="9", font_weight="bold", margin_bottom="0.25em", text_align="left"),
        rx.text("Publicado el " + AppState.comments.post.created_at_formatted, size="3", color_scheme="gray", margin_bottom="0.5em", text_align="left", width="100%"),
        rx.text(AppState.comments.formatted_price, size="7", color="gray", text_align="left"),
        rx.text(AppState.comments.content, size="5", margin_top="1em", white_space="pre-wrap", text_align="left"),
        _attributes_display(),
        _global_rating_display(),
        rx.spacer(),
        rx.button(
            "Añadir al Carrito",
            on_click=lambda: AppState.cart.add_to_cart(AppState.comments.post.id),
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
                color=rx.cond(i < AppState.comments.new_comment_rating, "gold", rx.color("gray", 8)),
                on_click=lambda: AppState.comments.set_new_comment_rating(i + 1),
                cursor="pointer",
                size=32,
            )
        ),
        spacing="2",
        padding_y="0.5em",
    )

def _star_rating_display(rating: rx.Var[int]) -> rx.Component:
    """Componente para mostrar una calificación con estrellas."""
    return rx.hstack(
        rx.foreach(
            rx.Var.range(5),
            lambda i: rx.icon(tag="star", color=rx.cond(i < rating, "gold", rx.color("gray", 8)), size=22)
        ),
        spacing="1"
    )

def _comment_form() -> rx.Component:
    """Formulario para añadir un nuevo comentario."""
    return rx.cond(
        AppState.is_authenticated,
        rx.cond(
            AppState.comments.user_can_comment,
            rx.form(
                rx.vstack(
                    rx.text("Tu calificación:", weight="bold", size="4"),
                    _star_rating_input(),
                    rx.text_area(name="comment_text", value=AppState.comments.new_comment_text, on_change=AppState.comments.set_new_comment_text, placeholder="Escribe tu opinión sobre el producto...", width="100%", size="3"),
                    rx.button("Publicar Opinión", type="submit", align_self="flex-end", size="3", color_scheme="violet"),
                    spacing="3", width="100%",
                ),
                on_submit=AppState.comments.add_comment, width="100%",
            ),
            # Mensajes para usuarios que no pueden comentar
            rx.box(
                rx.cond(
                    AppState.comments.user_has_commented,
                    rx.text("Ya has publicado una opinión para este producto.", size="4"),
                    rx.text("Debes haber comprado este producto para poder dejar tu opinión.", size="4")
                ),
                padding="1.5em", border="1px solid #444", border_radius="md", text_align="center", width="100%",
            )
        ),
        # Mensaje para usuarios no autenticados
        rx.box(
            rx.text("Debes ", rx.link("iniciar sesión", href="/login"), " y comprar este producto para poder comentarlo.", size="4"),
            padding="1.5em", border="1px solid #444", border_radius="md", text_align="center", width="100%",
        )
    )

def _comment_card(comment: CommentModel) -> rx.Component:
    """Tarjeta para mostrar un comentario individual."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.avatar(fallback=comment.userinfo.user.username[0], size="3"),
                    rx.text(comment.userinfo.user.username, weight="bold", size="4"),
                    _star_rating_display(comment.rating),
                    align="center",
                    spacing="3",
                ),
                rx.spacer(),
                rx.text(comment.created_at_formatted, size="3", color_scheme="gray"),
                align="center",
                width="100%",
            ),
            rx.text(comment.content, padding_left="3em", padding_top="0.5em", font_size="1.1em"),
            rx.cond(
                AppState.is_authenticated,
                rx.hstack(
                    rx.icon_button(rx.icon("thumbs-up", size=20), on_click=lambda: AppState.comments.handle_vote(comment.id, "like"), variant="soft"),
                    rx.text(comment.likes, size="3"),
                    rx.icon_button(rx.icon("thumbs-down", size=20), on_click=lambda: AppState.comments.handle_vote(comment.id, "dislike"), variant="soft"),
                    rx.text(comment.dislikes, size="3"),
                    spacing="2", align="center", padding_left="3em",
                )
            ),
            spacing="2", align="start",
        ),
        padding="1.5em", border_radius="md", bg=rx.color("gray", 2), width="100%",
    )

def comment_section() -> rx.Component:
    """Sección completa de comentarios."""
    return rx.vstack(
        rx.divider(margin_y="2em"),
        rx.heading("Opiniones del Producto", size="8", color_scheme="violet"),
        _comment_form(),
        rx.vstack(
            rx.foreach(AppState.comments.comments, _comment_card),
            spacing="4", width="100%", margin_top="1.5em",
        ),
        rx.cond(
            ~AppState.comments.comments,
            rx.center(rx.text("Sé el primero en dejar tu opinión.", color_scheme="gray", size="4"), padding="2em", width="100%")
        ),
        spacing="5", width="100%", max_width="1120px", align="center", padding_top="1em",
    )
    
def blog_public_detail_content() -> rx.Component:
    """Página que muestra el detalle de una publicación pública."""
    return rx.center(
        rx.vstack(
            rx.heading("Detalle del Producto", size="9", margin_bottom="1em", color_scheme="violet"),
            rx.cond(
                AppState.comments.post,
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
                        AppState.is_hydrated,
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