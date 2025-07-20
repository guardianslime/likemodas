# likemodas/blog/public_detail.py (VERSIÓN CORREGIDA FINAL)

import reflex as rx
from .state import CommentState, SessionState
from ..ui.carousel import carousel
from ..cart.state import CartState
from ..models import CommentModel
from ..ui.base import public_layout # 👈 CORRECCIÓN: Importamos el layout correcto

# --- Sección de Imagen ---
def _image_section() -> rx.Component:
    # (Esta función no cambia, usa CommentState para obtener los datos)
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

# --- Sección de Información ---
def _info_section() -> rx.Component:
    # (Esta función no cambia, usa CommentState para obtener los datos)
    return rx.vstack(
        rx.text(CommentState.post.title, size="7", font_weight="bold", margin_bottom="0.5em", text_align="left"),
        rx.text(CommentState.formatted_price, size="6", color="gray", text_align="left"),
        rx.text(CommentState.content, size="4", margin_top="1em", white_space="pre-wrap", text_align="left"),
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

# --- Componentes de Comentarios (sin cambios) ---
def _comment_form() -> rx.Component:
    """
    Formulario de comentarios que ahora maneja tres casos:
    1. No logueado -> Mensaje para iniciar sesión.
    2. Logueado, pero sin compra confirmada -> Mensaje para comprar.
    3. Logueado y con compra confirmada -> Formulario para comentar.
    """
    return rx.cond(
        SessionState.is_authenticated,
        # Si el usuario está logueado, verificamos si puede comentar
        rx.cond(
            CommentState.user_can_comment,
            # Caso 3: Sí puede comentar, mostramos el formulario
            rx.form(
                rx.vstack(
                    rx.text_area(name="comment_text", value=CommentState.new_comment_text, on_change=CommentState.set_new_comment_text, placeholder="Escribe tu opinión sobre el producto...", width="100%"),
                    rx.button("Publicar Opinión", type="submit", align_self="flex-end"),
                    spacing="3", width="100%",
                ),
                on_submit=CommentState.add_comment, width="100%",
            ),
            # Caso 2: No puede comentar, mostramos mensaje de compra
            rx.box(
                rx.text("Debes haber comprado este producto para poder dejar tu opinión."),
                padding="1.5em", border="1px solid #444", border_radius="md", text_align="center", width="100%",
            )
        ),
        # Caso 1: No está logueado, mostramos mensaje para iniciar sesión
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
                rx.cond(
                    SessionState.is_authenticated,
                    rx.hstack(
                        rx.icon_button(rx.icon("thumbs-up", size=18), on_click=lambda: CommentState.handle_vote(comment.id, "like"), variant="soft"),
                        rx.text(comment.likes, size="2"),
                        rx.icon_button(rx.icon("thumbs-down", size=18), on_click=lambda: CommentState.handle_vote(comment.id, "dislike"), variant="soft"),
                        rx.text(comment.dislikes, size="2"),
                        spacing="2", align="center",
                    )
                ),
                align="center",
            ),
            rx.text(comment.content, padding_left="2.5em", padding_top="0.5em"),
            spacing="2", align="start",
        ),
        padding="1em", border_radius="md", bg=rx.color("gray", 2), width="100%",
    )

def comment_section() -> rx.Component:
    return rx.vstack(
        rx.divider(margin_y="2em"),
        rx.heading("Comentarios", size="7"),
        _comment_form(),
        rx.vstack(
            rx.foreach(CommentState.comments, _comment_card),
            spacing="4", width="100%", margin_top="1.5em",
        ),
        rx.cond(
            ~CommentState.comments,
            rx.center(rx.text("Sé el primero en comentar.", color_scheme="gray"), padding="2em", width="100%")
        ),
        spacing="5", width="100%", max_width="900px", align="center", padding_top="1em",
    )

# --- Página Principal ---
def blog_public_detail_page() -> rx.Component:
    """Página que muestra el detalle de una publicación pública."""
    
    # --- 👇 CAMBIO ÚNICO Y CLAVE AQUÍ ---
    # En lugar de comprobar 'CommentState.has_post', comprobamos directamente 'CommentState.post'
    content_grid = rx.cond(
        CommentState.post, # ANTES: CommentState.has_post
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
            comment_section(), # Se añade la sección de comentarios
            spacing="6",
            width="100%",
            padding="2em",
            align="center",
        ),
        width="100%",
    )
    
    # 👈 CORRECCIÓN: Usamos el layout público importado de ui.base
    return public_layout(page_content)