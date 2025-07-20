# likemodas/blog/public_detail.py (CÓDIGO CORREGIDO Y COMPLETO)

import reflex as rx
import reflex_local_auth
from..navigation.state import NavState
from .state import BlogViewState, CommentState
from .. import navigation
from ..navigation.device import NavDeviceState
from ..navigation.state import force_reload_go_to
from ..ui.base import fixed_color_mode_button
from ..ui.search_state import SearchState
from ..ui.nav import public_navbar # Importamos la public_navbar unificada
from ..ui.carousel import carousel 
from ..cart.state import CartState 

# Esta es la barra de navegación local, con el estilo correcto y la recarga forzada.
# ELIMINAMOS _detail_page_navbar() ya que usaremos public_navbar()
def _detail_page_navbar() -> rx.Component:
    """
    Una barra de navegación local que ahora es visual y funcionalmente idéntica
    a la `public_navbar` global, utilizando navegación SPA.
    """
    return rx.box(
        rx.hstack(
            # Lado Izquierdo: Menú y Logo (sin cambios estructurales)
            rx.hstack(
                rx.menu.root(
                    rx.menu.trigger(
                        rx.button(rx.icon("menu", size=24), variant="soft", size="3")
                    ),
                    rx.menu.content(
                        # --- CAMBIO 1: Lógica de Navegación Unificada ---
                        # Se reemplaza `force_reload_go_to` por los métodos de `NavState`
                        # para lograr una navegación SPA fluida y consistente.
                        rx.menu.item("Home", on_click=NavState.to_home),
                        rx.menu.item("Productos", on_click=NavState.to_pulic_galeri),
                        rx.menu.item("Pricing", on_click=NavState.to_pricing),
                        rx.menu.item("Contact", on_click=NavState.to_contact),
                        rx.menu.separator(),
                        rx.menu.item("Login", on_click=NavState.to_login),
                        rx.menu.item("Register", on_click=NavState.to_register),
                    ),
                ),
                rx.image(src="/logo.jpg", width="8em", height="auto", border_radius="md"),
                align="center",
                spacing="4",
            ),
            
            # Campo de búsqueda con estilos corregidos
            rx.input(
                placeholder="Buscar productos...",
                value=SearchState.search_term,
                on_change=SearchState.update_search,
                on_blur=SearchState.search_action,
                width=["60%", "65%", "70%", "72%"],
                height=["2.5em", "2.8em", "3em", "3.3em"],
                padding_x="4",
                border_radius="full",
                # --- CAMBIO 2: Corrección del Borde ---
                # Se añade `border_width` para resolver el fallo visual de "reducción de grosor".
                border_width="1px",
                # --- CAMBIO 3: Alineación del Tamaño de Fuente ---
                # Se añade `font_size` responsivo para una paridad visual completa.
                font_size=rx.breakpoints(sm="2", md="3", lg="3"),
            ),
            justify="between",
            align="center",
            width="100%",
        ),
        # Estilos del contenedor principal, ahora idénticos a `public_navbar`
        position="fixed",
        top="0",
        left="0",
        right="0",
        width="100%",
        padding="0.75rem 1rem",
        z_index="99",
        # --- CAMBIO 4: Estandarización del Fondo ---
        # Se utilizan los mismos valores de `public_navbar` para una apariencia perfecta.
        bg=rx.color_mode_cond("#ffffffF0", "#1D2330F0"),
        style={"backdrop_filter": "blur(10px)"},
        on_mount=NavDeviceState.on_mount,
    )

def standalone_public_layout(child: rx.Component) -> rx.Component:
    """Layout autónomo que usa la navbar local."""
    return rx.fragment(
        public_navbar(), # <--- CAMBIO: Ahora usa la public_navbar unificada
        rx.box(
            child,
            padding_y="2em",
            padding_top="6rem", # Asegura el padding correcto para la navbar fija
            width="100%",
            margin="0 auto",
        ),
        fixed_color_mode_button(),
    )

# --- PÁGINA DE DETALLE MODIFICADA ---
def blog_public_detail_page() -> rx.Component:
    """Página que muestra el detalle de una publicación pública."""
    
    # Este es el contenido principal de la página (la imagen y la información).
    content_grid = rx.cond(
        BlogViewState.has_post,
        rx.grid(
            _image_section(),
            _info_section(),
            columns={"base": "1", "md": "2"},
            spacing="4",
            align_items="start",
            width="100%",
            max_width="1120px", # Se añade un ancho máximo
        ),
        rx.center(rx.text("Publicación no encontrada.", color="red"))
    )
    
    # ✨ CAMBIO: Se envuelve el contenido en una estructura centrada con título.
    # Esto imita el layout de la página de la galería.
    page_content = rx.center(
        rx.vstack(
            rx.heading("Detalle del Producto", size="8", margin_bottom="1em"),
            content_grid,
            spacing="6",
            width="100%",
            padding="2em",
            align="center",
        ),
        width="100%",
    )
    
    return standalone_public_layout(page_content)


# --- Componentes de la sección de imagen e información (SIN CAMBIOS) ---
def _image_section() -> rx.Component:
    """
    Sección para el carrusel de imágenes, ahora usando react-responsive-carousel.
    """
    return rx.box(
        rx.cond(
            BlogViewState.post.images & (BlogViewState.post.images.length() > 0),
            # 👇 Usamos el nuevo componente 'carousel'
            carousel(
                rx.foreach(
                    BlogViewState.post.images,
                    # Cada imagen es un hijo directo del carrusel
                    lambda image_url: rx.image(
                        src=rx.get_upload_url(image_url),
                        width="100%",
                        height="auto",
                        max_height="550px",
                        object_fit="contain",
                    )
                ),
                # Configuramos el carrusel
                show_indicators=True,
                infinite_loop=True,
                emulate_touch=True, # Clave para que funcione con el mouse
                show_thumbs=False,  # Ocultamos las miniaturas de abajo
            ),
            # Mensaje si no hay imágenes
            rx.image(
                src="/no_image.png",
                width="100%",
                height="auto",
                max_height="550px",
                object_fit="contain",
                border_radius="md",
            )
        ),
        width="100%",
        max_width="600px",
        position="relative",
    )

def _info_section() -> rx.Component:
    return rx.vstack(
        rx.text(BlogViewState.post.title, size="7", font_weight="bold", margin_bottom="0.5em", text_align="left"),
        rx.text(BlogViewState.formatted_price, size="6", color="gray", text_align="left"),
        rx.text(BlogViewState.content, size="4", margin_top="1em", white_space="pre-wrap", text_align="left"),
        rx.spacer(), # Empuja el botón hacia abajo
        rx.button(
            "Añadir al Carrito",
            on_click=lambda: CartState.add_to_cart(BlogViewState.post.id),
            width="100%",
            size="3",
            margin_top="1.5em", # Añade un poco de espacio arriba
        ),
        padding="1em",
        align="start",
        width="100%",
    )

def _comment_form() -> rx.Component:
    """Formulario para que usuarios registrados dejen un comentario."""
    return rx.cond(
        SessionState.is_authenticated,
        rx.form(
            rx.vstack(
                rx.text_area(
                    name="comment_text",
                    value=CommentState.new_comment_text,
                    on_change=CommentState.set_new_comment_text,
                    placeholder="Escribe tu comentario...",
                    width="100%",
                ),
                rx.button("Publicar Comentario", type="submit", align_self="flex-end"),
                spacing="3",
                width="100%",
            ),
            on_submit=CommentState.add_comment,
            width="100%",
        ),
        rx.box(
            rx.text("Debes ", rx.link("iniciar sesión", href="/login"), " para poder comentar."),
            padding="1.5em",
            border="1px solid #444",
            border_radius="md",
            text_align="center",
            width="100%",
        )
    )

def _comment_card(comment: CommentModel) -> rx.Component:
    """Componente visual para mostrar un único comentario."""
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
                # --- Votos (Like/Dislike) ---
                rx.cond(
                    SessionState.is_authenticated,
                    rx.hstack(
                        rx.icon_button(
                            rx.icon("thumbs-up", size=18),
                            on_click=lambda: CommentState.handle_vote(comment.id, "like"),
                            variant="soft",
                        ),
                        rx.text(comment.likes, size="2"),
                        rx.icon_button(
                            rx.icon("thumbs-down", size=18),
                            on_click=lambda: CommentState.handle_vote(comment.id, "dislike"),
                            variant="soft",
                        ),
                        rx.text(comment.dislikes, size="2"),
                        spacing="2",
                        align="center",
                    )
                ),
                align="center",
            ),
            rx.text(comment.content, padding_left="2.5em", padding_top="0.5em"),
            spacing="2",
            align="start",
        ),
        padding="1em",
        border_radius="md",
        bg=rx.color("gray", 2),
        width="100%",
    )

def comment_section() -> rx.Component:
    """Sección completa de comentarios que incluye el formulario y la lista."""
    return rx.vstack(
        rx.divider(margin_y="2em"),
        rx.heading("Comentarios", size="7"),
        _comment_form(),
        rx.vstack(
            rx.foreach(CommentState.comments, _comment_card),
            spacing="4",
            width="100%",
            margin_top="1.5em",
        ),
        rx.cond(
            ~CommentState.comments,
            rx.center(
                rx.text("Sé el primero en comentar.", color_scheme="gray"),
                padding="2em",
                width="100%",
            )
        ),
        spacing="5",
        width="100%",
        max_width="900px", # Ancho máximo para legibilidad
        align="center",
        padding_top="1em",
    )