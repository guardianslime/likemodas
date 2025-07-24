# likemodas/blog/public_detail.py (VERSIÓN CON TAMAÑOS AJUSTADOS)

import reflex as rx
from .state import CommentState, SessionState
from ..ui.carousel import carousel
from ..cart.state import CartState
from ..models import CommentModel
from ..ui.base import base_page
import math

# --- Sección de Imagen (sin cambios) ---
def _image_section() -> rx.Component:
    return rx.box(
        rx.cond(
            CommentState.post.images & (CommentState.post.images.length() > 0),
            carousel(
                rx.foreach(CommentState.post.images, lambda image_url: rx.image(src=rx.get_upload_url(image_url), width="100%", height="auto", max_height="550px", object_fit="contain")),
                show_indicators=True, infinite_loop=True, emulate_touch=True, show_thumbs=False
            ),
            rx.image(src="/no_image.png", width="100%", height="auto", max_height="550px", object_fit="contain", border_radius="md")
        ),
        width="100%", max_width="600px", position="relative",
    )

def _global_rating_display() -> rx.Component:
    """Muestra la calificación promedio global, incluyendo medias estrellas."""
    average_rating = CommentState.average_rating
    rating_count = CommentState.rating_count
    
    full_stars = rx.Var.range(math.floor(average_rating))
    has_half_star = (average_rating - math.floor(average_rating)) >= 0.5
    empty_stars = rx.Var.range(5 - math.ceil(average_rating))

    return rx.cond(
        rating_count > 0,
        rx.hstack(
            rx.foreach(full_stars, lambda _: rx.icon("star", color="gold", size=30)), # ✨ CAMBIO: size de 24 a 30
            rx.cond(has_half_star, rx.icon("star_half", color="gold", size=30), rx.fragment()), # ✨ CAMBIO: size de 24 a 30
            rx.foreach(empty_stars, lambda _: rx.icon("star", color=rx.color("gray", 8), size=30)), # ✨ CAMBIO: size de 24 a 30
            
            rx.text(
                f"{average_rating:.1f} de 5",
                size="4", # ✨ CAMBIO: size de 3 a 4
                weight="bold",
                margin_left="0.5em"
            ),
            rx.text(
                f"({rating_count} opiniones)",
                size="4", # ✨ CAMBIO: size de 3 a 4
                color_scheme="gray"
            ),
            align="center",
            spacing="1",
            padding_y="1em"
        ),
        rx.box(
            rx.text("Este producto aún no tiene calificaciones.", color_scheme="gray", size="4"), # ✨ CAMBIO: size añadido
            padding_y="1em"
        )
    )

def _info_section() -> rx.Component:
    return rx.vstack(
        rx.text(CommentState.post.title, size="9", font_weight="bold", margin_bottom="0.25em", text_align="left"),
        
        # --- 👇 LÍNEA AÑADIDA PARA MOSTRAR LA FECHA DE PUBLICACIÓN 👇 ---
        rx.text(
            "Publicado el " + CommentState.post.created_at_formatted,
            size="3",
            color_scheme="gray",
            margin_bottom="0.5em",
            text_align="left",
            width="100%"
        ),
        
        rx.text(CommentState.formatted_price, size="7", color="gray", text_align="left"),
        rx.text(CommentState.content, size="5", margin_top="1em", white_space="pre-wrap", text_align="left"),
        _global_rating_display(),
        rx.spacer(),
        rx.button(
            "Añadir al Carrito",
            on_click=lambda: CartState.add_to_cart(CommentState.post.id),
            width="100%",
            size="4",
            margin_top="1.5em",
        ),
        padding="1em",
        align="start",
        width="100%",
        min_height="350px",
    )

def _star_rating_input() -> rx.Component:
    return rx.hstack(
        rx.foreach(
            rx.Var.range(5),
            lambda i: rx.icon(
                tag="star",
                color=rx.cond(i < CommentState.new_comment_rating, "gold", rx.color("gray", 8)),
                on_click=lambda: CommentState.set_new_comment_rating(i + 1),
                cursor="pointer",
                size=32, # ✨ CAMBIO: size de 28 a 32
            )
        ),
        spacing="2",
        padding_y="0.5em",
    )

def _star_rating_display(rating: rx.Var[int]) -> rx.Component:
    return rx.hstack(
        rx.foreach(
            rx.Var.range(5),
            lambda i: rx.icon(
                tag="star",
                color=rx.cond(i < rating, "gold", rx.color("gray", 8)),
                size=22, # ✨ CAMBIO: size de 18 a 22
            )
        ),
        spacing="1"
    )

def _comment_form() -> rx.Component:
    return rx.cond(
        SessionState.is_authenticated,
        rx.cond(
            CommentState.user_can_comment,
            rx.form(
                rx.vstack(
                    rx.text("Tu calificación:", weight="bold", size="4"), # ✨ CAMBIO: size añadido
                    _star_rating_input(),
                    rx.text_area(name="comment_text", value=CommentState.new_comment_text, on_change=CommentState.set_new_comment_text, placeholder="Escribe tu opinión sobre el producto...", width="100%", size="3"), # ✨ CAMBIO: size añadido
                    rx.button("Publicar Opinión", type="submit", align_self="flex-end", size="3"), # ✨ CAMBIO: size añadido
                    spacing="3", width="100%",
                ),
                on_submit=CommentState.add_comment, width="100%",
            ),
            rx.box(
                rx.cond(
                    CommentState.user_has_commented,
                    rx.text("Ya has publicado una opinión para este producto.", size="4"), # ✨ CAMBIO: size añadido
                    rx.text("Debes haber comprado este producto para poder dejar tu opinión.", size="4") # ✨ CAMBIO: size añadido
                ),
                padding="1.5em", border="1px solid #444", border_radius="md", text_align="center", width="100%",
            )
        ),
        rx.box(
            rx.text("Debes ", rx.link("iniciar sesión", href="/login"), " y comprar este producto para poder comentarlo.", size="4"), # ✨ CAMBIO: size añadido
            padding="1.5em", border="1px solid #444", border_radius="md", text_align="center", width="100%",
        )
    )

def _comment_card(comment: CommentModel) -> rx.Component:
    return rx.box(
        rx.vstack(
            # --- SECCIÓN SUPERIOR DEL COMENTARIO (MODIFICADA) ---
            rx.hstack(
                # Grupo izquierdo: Avatar, Nombre y ESTRELLAS
                rx.hstack(
                    rx.avatar(fallback=comment.userinfo.user.username[0], size="3"),
                    rx.text(comment.userinfo.user.username, weight="bold", size="4"),
                    # --- ESTRELLAS MOVIDAS AQUÍ ---
                    _star_rating_display(comment.rating),
                    align="center",
                    spacing="3", # Aumentamos el espaciado para que se vea mejor
                ),
                rx.spacer(), # El espaciador empuja la fecha hacia la derecha
                # --- FECHA MOVIDA A LA DERECHA ---
                rx.text(
                    comment.created_at_formatted, # Quitamos el "•"
                    size="3",
                    color_scheme="gray"
                ),
                align="center",
                width="100%",
            ),
            
            rx.text(comment.content, padding_left="3em", padding_top="0.5em", font_size="1.1em"), # ✨ CAMBIOS: padding y font_size
            rx.cond(
                SessionState.is_authenticated,
                rx.hstack(
                    rx.icon_button(rx.icon("thumbs-up", size=20), on_click=lambda: CommentState.handle_vote(comment.id, "like"), variant="soft"), # ✨ CAMBIO: size de 18 a 20
                    rx.text(comment.likes, size="3"), # ✨ CAMBIO: size de 2 a 3
                    rx.icon_button(rx.icon("thumbs-down", size=20), on_click=lambda: CommentState.handle_vote(comment.id, "dislike"), variant="soft"), # ✨ CAMBIO: size de 18 a 20
                    rx.text(comment.dislikes, size="3"), # ✨ CAMBIO: size de 2 a 3
                    spacing="2", align="center", padding_left="3em", # ✨ CAMBIO: padding
                )
            ),
            spacing="2", align="start",
        ),
        padding="1.5em", border_radius="md", bg=rx.color("gray", 2), width="100%", # ✨ CAMBIO: padding
    )

def comment_section() -> rx.Component:
    return rx.vstack(
        rx.divider(margin_y="2em"),
        rx.heading("Opiniones del Producto", size="8"), # ✨ CAMBIO: size de 7 a 8
        _comment_form(),
        rx.vstack(
            rx.foreach(CommentState.comments, _comment_card),
            spacing="4", width="100%", margin_top="1.5em",
        ),
        rx.cond(
            ~CommentState.comments,
            rx.center(rx.text("Sé el primero en dejar tu opinión.", color_scheme="gray", size="4"), padding="2em", width="100%") # ✨ CAMBIO: size añadido
        ),
        spacing="5", 
        width="100%", 
        max_width="1120px", # ✨ CAMBIO: max_width de 900px a 1120px
        align="center", 
        padding_top="1em",
    )

def blog_public_detail_page() -> rx.Component:
    """Página que muestra el detalle de una publicación pública."""
    content_grid = rx.cond(
        CommentState.post,
        rx.grid(
            _image_section(),
            _info_section(),
            columns={"base": "1", "md": "2"},
            spacing="4",
            align_items="start",
            width="100%",
            max_width="1400px", # ✨ CAMBIO: max_width de 1120px a 1400px
        ),
        rx.center(rx.text("Publicación no encontrada.", color="red"))
    )
    
    page_content = rx.center(
        rx.vstack(
            rx.heading("Detalle del Producto", size="9", margin_bottom="1em"), # ✨ CAMBIO: size de 8 a 9
            content_grid,
            comment_section(),
            spacing="6",
            width="100%",
            padding="2em",
            align="center",
        ),
        width="100%",
    )
    
    return base_page(page_content)