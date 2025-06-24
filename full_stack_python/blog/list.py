import reflex as rx 
import reflex_local_auth
from .. import navigation
from ..ui.base import base_page
from ..models import BlogPostModel
from . import state

def blog_post_detail_link(child: rx.Component, post: BlogPostModel):
    return rx.cond(
        post & post.id,
        rx.link(
            child,
            href=f"{navigation.routes.BLOG_POSTS_ROUTE}/{post.id}"
        ),
        rx.fragment(child)
    )

# --- Componente para la lista PRIVADA del usuario ---
def blog_post_list_item(post: BlogPostModel):
    return rx.box(
        blog_post_detail_link(    
            rx.heading(post.title, size="5"),
            post
        ),
        # --- CORRECCIÓN CLAVE ---
        # No se puede usar .strftime() en una rx.Var.
        # Usamos .to_string() para formatear la fecha correctamente en la UI.
        rx.text("Creado el: ", rx.text(post.created_at.to_string(date_style="short"))),
        
        rx.text(
            rx.cond(post.publish_active, "Publicado", "Borrador"),
            color_scheme=rx.cond(post.publish_active, "green", "orange"),
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

# --- Componente para la lista PÚBLICA ---
def blog_public_card(post: BlogPostModel):
    return rx.card(
        blog_post_detail_link(
            rx.flex(
                rx.box(
                    rx.heading(post.title, size="4"),
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
        on_mount=state.ArticlePublicState.set_limit_and_load(limit)
    )
