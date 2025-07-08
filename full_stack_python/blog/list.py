# full_stack_python/blog/list.py (CORREGIDO)

import reflex as rx
import reflex_local_auth
from .. import navigation
from ..ui.base import base_page
from ..models import BlogPostModel
from . import state

def blog_post_detail_link(child: rx.Component, post: BlogPostModel):
    # Primero, las guardas para post y post.id
    if post is None or post.id is None:
        return rx.fragment(child)
    
    post_detail_url = f"{navigation.routes.BLOG_POSTS_ROUTE}/{post.id}"
    
    return rx.link(
        child,
        # --- CORRECCIÓN CLAVE ---
        # Verificamos que post.userinfo exista antes de intentar acceder a .email
        rx.cond(
            post.userinfo,
            rx.heading("by ", post.userinfo.email),
            rx.heading("by Anonymous") # Fallback por si no hay autor
        ),
        href=post_detail_url
    )

def blog_post_list_item(post: BlogPostModel):
    return rx.box(
        blog_post_detail_link(
            rx.heading(post.title),
            post
        ),
        padding="1em"
    )

@reflex_local_auth.require_login
def blog_post_list_page() -> rx.Component:
    return base_page(
        rx.vstack(
            rx.heading("Blog Posts", size="5"),
            rx.link(
                rx.button("New Post"),
                href=navigation.routes.BLOG_POST_ADD_ROUTE
            ),
            rx.foreach(state.BlogPostState.posts, blog_post_list_item),
            spacing="5",
            align="center",
            min_height="85vh",
        )
    )