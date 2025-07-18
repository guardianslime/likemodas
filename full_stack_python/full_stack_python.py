# full_stack_python/full_stack_python.py (CORREGIDO Y COMPLETO)

import reflex as rx
import reflex_local_auth

from full_stack_python.blog.public_detail import blog_public_detail_page
from full_stack_python.blog.page import blog_public_page
from full_stack_python.blog.state import BlogViewState, BlogPostState
from rxconfig import config

# --- Módulos y Componentes ---
from .ui.base import base_page
from .auth.pages import my_login_page, my_register_page, my_logout_page
from .auth.state import SessionState

from .cart.page import cart_page
from .cart.state import CartState
from .purchases.page import purchase_history_page
from .purchases.state import PurchaseHistoryState
from .admin.page import admin_confirm_page
from .admin.state import AdminConfirmState

from .articles.detail import article_detail_page, ArticleDetailState
from .articles.list import articles_public_gallery_page
from .articles.state import ArticlePublicState

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
    ),
)

# --- Registro de Páginas ---

app.add_page(index, on_load=ArticlePublicState.load_posts)
app.add_page(my_login_page, route=reflex_local_auth.routes.LOGIN_ROUTE)
app.add_page(my_register_page, route=reflex_local_auth.routes.REGISTER_ROUTE)
app.add_page(my_logout_page, route=navigation.routes.LOGOUT_ROUTE)
app.add_page(pages.about_page, route=navigation.routes.ABOUT_US_ROUTE)
app.add_page(pages.protected_page, route="/protected/", on_load=SessionState.on_load)
app.add_page(pages.pricing_page, route=navigation.routes.PRICING_ROUTE)


# --- Páginas de E-commerce ---
app.add_page(
    cart_page,
    route="/cart",
    title="Mi Carrito"
)

app.add_page(
    purchase_history_page,
    route="/my-purchases",
    title="Mis Compras",
    on_load=PurchaseHistoryState.load_purchases
)

app.add_page(
    admin_confirm_page,
    route="/admin/confirm-payments",
    title="Confirmar Pagos",
    on_load=AdminConfirmState.load_pending_purchases
)


# --- Páginas de Artículos (Existentes) ---
app.add_page(
    articles_public_gallery_page,
    route=navigation.routes.ARTICLE_LIST_ROUTE,
    on_load=ArticlePublicState.load_posts,
)
app.add_page(
    article_detail_page,
    route=f"{navigation.routes.ARTICLE_LIST_ROUTE}/[article_id]",
    on_load=ArticleDetailState.on_load,
)

# --- Páginas de Blog (Privadas del Admin) ---
app.add_page(
    blog.blog_post_list_page,
    route=navigation.routes.BLOG_POSTS_ROUTE,
    on_load=BlogPostState.load_posts
)
app.add_page(
    blog.blog_post_detail_page,
    route=f"{navigation.routes.BLOG_POSTS_ROUTE}/[blog_id]",
    on_load=BlogPostState.get_post_detail,
)
app.add_page(blog.blog_post_add_page, route=navigation.routes.BLOG_POST_ADD_ROUTE)
app.add_page(
    blog.blog_post_edit_page,
    route="/blog/[blog_id]/edit",
    on_load=blog.BlogEditFormState.on_load_edit
)

# --- Página de la galería pública ---
app.add_page(
    blog_public_page,
    route=navigation.routes.BLOG_PUBLIC_PAGE_ROUTE,
    title="Galería pública",
    # --- ✨ CORRECCIÓN: Se usa CartState para cargar los posts ---
    on_load=CartState.on_load
)

# --- Página de detalle público ---
app.add_page(
    blog_public_detail_page,
    route=f"{navigation.routes.BLOG_PUBLIC_DETAIL_ROUTE}/[blog_public_id]",
    title="Detalle de la Publicación",
    on_load=BlogViewState.on_load
)

# --- Páginas de Contacto ---
app.add_page(contact.contact_page, route=navigation.routes.CONTACT_US_ROUTE)
app.add_page(
    contact.contact_entries_list_page,
    route=navigation.routes.CONTACT_ENTRIES_ROUTE,
    on_load=contact.ContactState.load_entries
)