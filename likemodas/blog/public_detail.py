# likemodas/blog/public_detail.py (VERSIÓN ACTUALIZADA)

import reflex as rx
from .state import CommentState, SessionState
from ..ui.carousel import carousel
from ..cart.state import CartState
from ..models import CommentModel
from ..ui.base import public_layout
import math

# --- Sección de Imagen (no cambia) ---
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

# --- ✨ CAMBIOS AQUÍ ---

# ✨ 1. NUEVO COMPONENTE: Para mostrar la calificación global con medias estrellas
def _global_rating_display() -> rx.Component:
    """Muestra la calificación promedio global, incluyendo medias estrellas."""
    average_rating = CommentState.post.average_rating
    # Usamos math.floor para obtener la parte entera del promedio
    full_stars = rx.Var.range(average_rating.floor())
    # Verificamos si hay media estrella
    has_half_star = (average_rating - average_rating.floor()) >= 0.5
    # Calculamos el número de estrellas vacías
    empty_stars = rx.Var.range(5 - average_rating.ceil())

    return rx.cond(
        CommentState.post.rating_count > 0,
        rx.hstack(
            # Estrellas llenas
            rx.foreach(full_stars, lambda: rx.icon("star", color="gold", size=24)),
            # Media estrella (si aplica)
            rx.cond(has_half_star, rx.icon("star_half", color="gold", size=24), rx.fragment()),
            # Estrellas vacías
            rx.foreach(empty_stars, lambda: rx.icon("star", color=rx.color("gray", 8), size=24)),
            
            rx.text(
                f"{average_rating:.1f} de 5",
                size="3",
                weight="bold",
                margin_left="0.5em"
            ),
            rx.text(
                f"({CommentState.post.rating_count} opiniones)",
                size="3",
                color_scheme="gray"
            ),
            align="center",
            spacing="1",
            padding_y="1em"
        ),
        rx.box(
            rx.text("Este producto aún no tiene calificaciones.", color_scheme="gray"),
            padding_y="1em"
        )
    )

# ✨ 2. MODIFICACIÓN: Se añade el componente de calificación global a la info del producto
def _info_section() -> rx.Component:
    return rx.vstack(
        rx.text(CommentState.post.title, size="7", font_weight="bold", margin_bottom="0.5em", text_align="left"),
        rx.text(CommentState.formatted_price, size="6", color="gray", text_align="left"),
        rx.text(CommentState.content, size="4", margin_top="1em", white_space="pre-wrap", text_align="left"),
        
        # --- LÍNEA AÑADIDA ---
        _global_rating_display(), # Se muestra la calificación global aquí
        
        rx.spacer(),
        rx.button(
            "Añadir al Carrito",
            on_click=lambda: CartState.add_to_cart(CommentState.post.id),
            width="100%",
            size="3",
            margin_top="1.5em",
        ),
        padding="1em",
        align="start",
        width="100%",
        min_height="350px",
    )
# --- FIN DE CAMBIOS ---

# (El resto de los componentes de comentarios no cambian)
def _star_rating_input() -> rx.Component:
    return rx.hstack(
        rx.foreach(
            rx.Var.range(5),
            lambda i: rx.icon(
                tag="star",
                color=rx.cond(i < CommentState.new_comment_rating, "gold", rx.color("gray", 8)),
                on_click=lambda: CommentState.set_new_comment_rating(i + 1),
                cursor="pointer",
                size=28,
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
                size=18,
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
                    rx.text("Tu calificación:", weight="bold"),
                    _star_rating_input(),
                    rx.text_area(name="comment_text", value=CommentState.new_comment_text, on_change=CommentState.set_new_comment_text, placeholder="Escribe tu opinión sobre el producto...", width="100%"),
                    rx.button("Publicar Opinión", type="submit", align_self="flex-end"),
                    spacing="3", width="100%",
                ),
                on_submit=CommentState.add_comment, width="100%",
            ),
            rx.box(
                rx.cond(
                    CommentState.user_has_commented,
                    rx.text("Ya has publicado una opinión para este producto."),
                    rx.text("Debes haber comprado este producto para poder dejar tu opinión.")
                ),
                padding="1.5em", border="1px solid #444", border_radius="md", text_align="center", width="100%",
            )
        ),
        rx.box(
            rx.text("Debes ", rx.link("iniciar sesión", href="/login"), " y comprar este producto para poder comentarlo."),
            padding="1.5em", border="1px solid #444", border_radius="md", text_align="center", width="100%",
        )
    )

def _comment_card(comment: CommentModel) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.avatar(fallback=comment.userinfo.user.username[0], size="2"),
                    rx.text(comment.userinfo.user.username, weight="bold"),
                    rx.text(f"• {comment.created_at_formatted}", size="2", color_scheme="gray"),
                    align="center",
                ),
                rx.spacer(),
                _star_rating_display(comment.rating),
                align="center",
            ),
            rx.text(comment.content, padding_left="2.5em", padding_top="0.5em"),
            rx.cond(
                SessionState.is_authenticated,
                rx.hstack(
                    rx.icon_button(rx.icon("thumbs-up", size=18), on_click=lambda: CommentState.handle_vote(comment.id, "like"), variant="soft"),
                    rx.text(comment.likes, size="2"),
                    rx.icon_button(rx.icon("thumbs-down", size=18), on_click=lambda: CommentState.handle_vote(comment.id, "dislike"), variant="soft"),
                    rx.text(comment.dislikes, size="2"),
                    spacing="2", align="center", padding_left="2.5em",
                )
            ),
            spacing="2", align="start",
        ),
        padding="1em", border_radius="md", bg=rx.color("gray", 2), width="100%",
    )

def comment_section() -> rx.Component:
    return rx.vstack(
        rx.divider(margin_y="2em"),
        rx.heading("Opiniones del Producto", size="7"),
        _comment_form(),
        rx.vstack(
            rx.foreach(CommentState.comments, _comment_card),
            spacing="4", width="100%", margin_top="1.5em",
        ),
        rx.cond(
            ~CommentState.comments,
            rx.center(rx.text("Sé el primero en dejar tu opinión.", color_scheme="gray"), padding="2em", width="100%")
        ),
        spacing="5", width="100%", max_width="900px", align="center", padding_top="1em",
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
            max_width="1120px",
        ),
        rx.center(rx.text("Publicación no encontrada.", color="red"))
    )
    
    page_content = rx.center(
        rx.vstack(
            rx.heading("Detalle del Producto", size="8", margin_bottom="1em"),
            content_grid,
            comment_section(),
            spacing="6",
            width="100%",
            padding="2em",
            align="center",
        ),
        width="100%",
    )
    
    return public_layout(page_content)