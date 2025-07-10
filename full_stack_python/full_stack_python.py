#full_stack_python/full_stack_python.py


"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx
import reflex_local_auth

from full_stack_python.blog.forms import blog_post_add_form
from full_stack_python.public_post.view import public_post_detail_page
from full_stack_python.public_post.state import BlogViewState
from full_stack_python.blog.page import blog_public_page
from full_stack_python.blog.state import BlogPublicState
from rxconfig import config

# --- Módulos y Componentes ---
from .ui.base import base_page
from .auth.pages import my_login_page, my_register_page, my_logout_page
from .auth.state import SessionState
from .articles.detail import article_detail_page
from .articles.list import article_public_list_page
from .articles.state import ArticlePublicState

# Se importan los paquetes completos para usar la notación paquete.componente
from . import blog, contact, navigation, pages

# --- Definición de la Aplicación ---

def index() -> rx.Component:
    """La página principal que redirige al dashboard si el usuario está autenticado."""
    return base_page(
        rx.cond(
            SessionState.is_authenticated,
            pages.dashboard_component(),
            pages.landing_component(),
        )
    )

app = rx.App(
    theme=rx.theme(
        appearance="dark", 
        has_background=True, 
        panel_background="solid",
        scaling="90%",
        radius="medium",
        accent_color="sky"
    )
)

# --- Registro de Páginas ---

app.add_page(index, on_load=ArticlePublicState.load_posts)
app.add_page(my_login_page, route=reflex_local_auth.routes.LOGIN_ROUTE)
app.add_page(my_register_page, route=reflex_local_auth.routes.REGISTER_ROUTE)
app.add_page(my_logout_page, route=navigation.routes.LOGOUT_ROUTE)
app.add_page(pages.about_page, route=navigation.routes.ABOUT_US_ROUTE)
app.add_page(pages.protected_page, route="/protected/", on_load=SessionState.on_load)
app.add_page(pages.pricing_page, route=navigation.routes.PRICING_ROUTE)


# Páginas de Artículos
app.add_page(
    article_public_list_page,
    route=navigation.routes.ARTICLE_LIST_ROUTE,
    on_load=ArticlePublicState.load_posts,
)
app.add_page(
    article_detail_page,
    route=f"{navigation.routes.ARTICLE_LIST_ROUTE}/[article_id]",
    on_load=ArticlePublicState.get_post_detail,
)

# Páginas de Blog
app.add_page(
    blog.blog_post_list_page,
    route=navigation.routes.BLOG_POSTS_ROUTE,
    on_load=blog.BlogPostState.load_posts
)
app.add_page(blog.blog_post_add_page, route=navigation.routes.BLOG_POST_ADD_ROUTE)
app.add_page(
    blog.blog_post_detail_page,
    route="/blog/[blog_id]",
    on_load=blog.BlogPostState.get_post_detail
)
app.add_page(
    blog.blog_post_edit_page,
    route="/blog/[blog_id]/edit",
    on_load=blog.BlogPostState.get_post_detail
)
app.add_page(blog_public_page, route="/blog/page", title="Galería pública", on_load=BlogPublicState.on_load)
app.add_page(
    public_post_detail_page,
    route="/public-post/[public_post_id]",
    title="Publicación"
)


# Páginas de Contacto
app.add_page(contact.contact_page, route=navigation.routes.CONTACT_US_ROUTE)
app.add_page(
    contact.contact_entries_list_page,
    route=navigation.routes.CONTACT_ENTRIES_ROUTE,
    on_load=contact.ContactState.load_entries
)
