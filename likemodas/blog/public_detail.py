# likemodas/blog/public_detail.py (VERSIÓN CORREGIDA)

import reflex as rx
from ..navigation.state import NavState
from .state import CommentState, SessionState # Usar CommentState y SessionState
from ..ui.nav import public_navbar
from ..ui.carousel import carousel
from ..cart.state import CartState
from ..models import CommentModel # Importar el modelo de comentario
from ..ui.base import standalone_public_layout # Importar el layout específico

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

# --- Sección de Información (Corregida) ---
def _info_section() -> rx.Component:
    return rx.vstack(
        rx.text(CommentState.post.title, size="7", font_weight="bold", margin_bottom="0.5em", text_align="left"),
        rx.text(CommentState.formatted_price, size="6", color="gray", text_align="left"),
        rx.text(CommentState.content, size="4", margin_top="1em", white_space="pre-wrap", text_align="left"),
        rx.spacer(),
        rx.button(
            "Añadir al Carrito",
            # CORRECCIÓN: Usar CommentState para obtener el id del post
            on_click=lambda: CartState.add_to_cart(CommentState.post.id),
            width="100%",
            size="3",
            margin_top="1.5em",
        ),
        padding="1em",
        align="start",
        width="100%",
        min_height="350px", # Ayuda a alinear el botón verticalmente
    )

# --- Componentes de Comentarios (Los que ya tenías) ---
def _comment_form() -> rx.Component:
    return rx.cond(
        SessionState.is_authenticated,
        rx.form(
            rx.vstack(
                rx.text_area(name="comment_text", value=CommentState.new_comment_text, on_change=CommentState.set_new_comment_text, placeholder="Escribe tu comentario...", width="100%"),
                rx.button("Publicar Comentario", type="submit", align_self="flex-end"),
                spacing="3", width="100%",
            ),
            on_submit=CommentState.add_comment, width="100%",
        ),
        rx.box(
            rx.text("Debes ", rx.link("iniciar sesión", href="/login"), " para poder comentar."),
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


# --- Página Principal (Corregida para integrar todo) ---
def blog_public_detail_page() -> rx.Component:
    content_grid = rx.cond(
        CommentState.has_post,
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
            # INTEGRACIÓN: Aquí se añade la sección de comentarios
            comment_section(),
            spacing="6",
            width="100%",
            padding="2em",
            align="center",
        ),
        width="100%",
    )
    
    # Asegúrate de usar un layout que no dependa de base_page para evitar conflictos de estado
    # (standalone_public_layout es una buena práctica si lo tienes definido)
    return standalone_public_layout(page_content)