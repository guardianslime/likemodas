# likemodas/likemodas.py (VERSIÓN FINAL Y LIMPIA)

import reflex as rx
import reflex_local_auth

# --- Importaciones de Estados y Páginas ---
from rxconfig import config
from . import blog, contact, navigation, pages

# Estados
from .auth.state import SessionState
from .auth.reset_password_state import ResetPasswordState
from .auth.verify_state import VerifyState
# ✨ CAMBIO: Se eliminan los estados de articles
# from .articles.state import ArticleDetailState, ArticlePublicState 
from .blog.state import BlogPostState, CommentState
from .cart.state import CartState
from .purchases.state import PurchaseHistoryState
from .admin.state import AdminConfirmState, PaymentHistoryState

# Páginas
from .ui.base import base_page
from .auth.pages import my_login_page, my_register_page, my_logout_page, verification_page, forgot_password_page, reset_password_page
from .cart.page import cart_page
from .purchases.page import purchase_history_page
from .admin.page import admin_confirm_page, payment_history_page
# ✨ CAMBIO: Se eliminan las páginas de articles
# from .articles.detail import article_detail_page
# from .articles.list import articles_public_gallery_page
from .blog.page import blog_public_page
from .blog.public_detail import blog_public_detail_page
from .pages.search_results import search_results_page

# --- Definición de la Aplicación ---
def index() -> rx.Component:
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

# Páginas Generales y de Autenticación
# ✨ CAMBIO: La página de inicio ahora carga los datos con CartState.on_load
app.add_page(index, on_load=CartState.on_load)
app.add_page(search_results_page, route="/search-results", title="Resultados de Búsqueda")
app.add_page(my_login_page, route=reflex_local_auth.routes.LOGIN_ROUTE)
app.add_page(my_register_page, route=reflex_local_auth.routes.REGISTER_ROUTE)
app.add_page(verification_page, route="/verify-email", on_load=VerifyState.verify_token)
app.add_page(forgot_password_page, route="/forgot-password")
app.add_page(reset_password_page, route="/reset-password", on_load=ResetPasswordState.on_load_check_token)
app.add_page(my_logout_page, route=navigation.routes.LOGOUT_ROUTE)
app.add_page(pages.about_page, route=navigation.routes.ABOUT_US_ROUTE)
app.add_page(pages.pricing_page, route=navigation.routes.PRICING_ROUTE)

# ✨ CAMBIO: Se eliminan las páginas de articles
# app.add_page(articles_public_gallery_page, route=navigation.routes.ARTICLE_LIST_ROUTE, on_load=ArticlePublicState.load_posts)
# app.add_page(article_detail_page, route=f"{navigation.routes.ARTICLE_LIST_ROUTE}/[article_id]", on_load=ArticleDetailState.on_load)

# --- Páginas Públicas del Blog / Tienda ---
app.add_page(
    blog_public_page,
    route=navigation.routes.BLOG_PUBLIC_PAGE_ROUTE, # Ruta: "/blog/page"
    title="Galería de Productos",
    on_load=CartState.on_load # Ya estaba correcto, pero se confirma
)
app.add_page(
    blog_public_detail_page,
    route=f"{navigation.routes.BLOG_PUBLIC_DETAIL_ROUTE}/[blog_public_id]", # Ruta: "/blog-public/[id]"
    title="Detalle del Producto",
    on_load=CommentState.on_load
)

# --- Páginas de E-commerce del Usuario ---
app.add_page(cart_page, route="/cart", title="Mi Carrito")
app.add_page(purchase_history_page, route="/my-purchases", title="Mis Compras", on_load=PurchaseHistoryState.load_purchases)

# --- Páginas Privadas de Administración ---
app.add_page(blog.blog_post_list_page, route=navigation.routes.BLOG_POSTS_ROUTE, on_load=blog.BlogPostState.load_posts) # Ruta: "/blog"
app.add_page(blog.blog_post_detail_page, route=f"{navigation.routes.BLOG_POSTS_ROUTE}/[blog_id]", on_load=blog.BlogPostState.get_post_detail)
app.add_page(blog.blog_post_add_page, route=navigation.routes.BLOG_POST_ADD_ROUTE)
app.add_page(blog.blog_post_edit_page, route="/blog/[blog_id]/edit", on_load=blog.BlogEditFormState.on_load_edit)
app.add_page(admin_confirm_page, route="/admin/confirm-payments", title="Confirmar Pagos", on_load=AdminConfirmState.load_pending_purchases)
app.add_page(payment_history_page, route="/admin/payment-history", title="Historial de Pagos", on_load=PaymentHistoryState.load_confirmed_purchases)

# Páginas de Contacto
app.add_page(contact.contact_page, route=navigation.routes.CONTACT_US_ROUTE)
app.add_page(contact.contact_entries_list_page, route=navigation.routes.CONTACT_ENTRIES_ROUTE, on_load=contact.ContactState.load_entries)