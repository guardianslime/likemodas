import reflex as rx 
import reflex_local_auth
from .. import navigation
from ..ui.base import base_page
from ..models import BlogPostModel
from . import state

# --- Componente reutilizable para el enlace de detalle ---
def blog_post_detail_link(child: rx.Component, post: BlogPostModel):
    """
    Envuelve un componente en un enlace a la página de detalle del post.
    Usa rx.cond para manejar de forma segura el caso de que el post no exista.
    """
    return rx.cond(
        # Condición: El post y su ID deben existir.
        post & post.id,
        # Si la condición es verdadera, crea el enlace.
        rx.link(
            child,
            href=f"{navigation.routes.BLOG_POSTS_ROUTE}/{post.id}"
        ),
        # Si es falsa, muestra el componente hijo sin enlace.
        rx.fragment(child)
    )

# --- Componente para la lista PRIVADA del usuario ---
def blog_post_list_item(post: BlogPostModel):
    return rx.box(
        blog_post_detail_link(    
            rx.heading(post.title, size="5"),
            post
        ),
        rx.text(f"Creado el: {post.created_at.strftime('%d/%m/%Y')}"),
        rx.text(
            "Publicado" if post.publish_active else "Borrador",
            color_scheme="green" if post.publish_active else "orange",
        ),
        padding="1em",
        border="1px solid #444",
        border_radius="8px",
        width="100%"
    )

@reflex_local_auth.require_login
def blog_post_list_page() -> rx.Component:
    return base_page(
        rx.vstack(
            rx.heading("Mis Publicaciones", size="8"),
            rx.link(
                rx.button("Nueva Publicación"),
                href=navigation.routes.BLOG_POST_ADD_ROUTE
            ),
            rx.foreach(state.BlogPostState.posts, blog_post_list_item),
            spacing="5",
            align="center",
            width="100%",
            max_width="960px",
            padding_x="1em",
            min_height="85vh",
        )
    )

# --- Componente para la lista PÚBLICA (usado en el dashboard y landing page) ---
def blog_public_card(post: BlogPostModel):
    """Una tarjeta individual para un post público."""
    return rx.card(
        blog_post_detail_link(
            rx.flex(
                rx.box(
                    rx.heading(post.title, size="4"),
                    # Usamos rx.cond para la lógica condicional en la UI.
                    rx.cond(
                        post.userinfo,
                        rx.text(f"Por {post.userinfo.email}"),
                        rx.text("Autor desconocido")
                    ),
                ),
                spacing="2",
                direction="column",
                align="start"
            ),
            post
        ), 
        as_child=True,
        size="2"
    )

def blog_public_list_component(columns:int=3, spacing:int=5, limit:int=100) -> rx.Component:
    return rx.grid(
        rx.foreach(state.ArticlePublicState.posts, blog_public_card),
        columns=f'{columns}',
        spacing=f'{spacing}',
        width="100%",
        on_mount=lambda: state.ArticlePublicState.load_posts(limit=limit)
    )
