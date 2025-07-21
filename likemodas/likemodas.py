# likemodas/likemodas.py (VERSIÓN FINAL)

import reflex as rx
import reflex_local_auth

from rxconfig import config
# Se importan los MÓDULOS principales
from . import blog, contact, navigation, pages, admin, auth, cart, purchases

from .ui.base import base_page
from .auth.state import SessionState

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

# --- Se referencian todas las páginas y eventos on_load a través de sus rutas de módulo completas ---

# --- Páginas Generales y de Autenticación ---
app.add_page(index, on_load=cart.state.CartState.on_load)
app.add_page(pages.search_results.search_results_page, route="/search-results", title="Resultados de Búsqueda")
app.add_page(auth.pages.my_login_page, route=reflex_local_auth.routes.LOGIN_ROUTE)
app.add_page(auth.pages.my_register_page, route=reflex_local_auth.routes.REGISTER_ROUTE)
app.add_page(auth.pages.verification_page, route="/verify-email", on_load=auth.verify_state.VerifyState.verify_token)
app.add_page(auth.pages.forgot_password_page, route="/forgot-password")
app.add_page(auth.pages.reset_password_page, route="/reset-password", on_load=auth.reset_password_state.ResetPasswordState.on_load_check_token)
app.add_page(auth.pages.my_logout_page, route=navigation.routes.LOGOUT_ROUTE)
app.add_page(pages.about_page, route=navigation.routes.ABOUT_US_ROUTE)
app.add_page(pages.pricing_page, route=navigation.routes.PRICING_ROUTE)

# --- Páginas Públicas del Blog / Tienda ---
app.add_page(
    blog.page.blog_public_page,
    route=navigation.routes.BLOG_PUBLIC_PAGE_ROUTE,
    title="Galería de Productos",
    on_load=cart.state.CartState.on_load
)
app.add_page(
    blog.public_detail.blog_public_detail_page,
    route=f"{navigation.routes.BLOG_PUBLIC_DETAIL_ROUTE}/[blog_public_id]",
    title="Detalle del Producto",
    on_load=blog.state.CommentState.on_load
)

# --- Páginas de E-commerce del Usuario ---
app.add_page(cart.page.cart_page, route="/cart", title="Mi Carrito")
app.add_page(purchases.page.purchase_history_page, route="/my-purchases", title="Mis Compras", on_load=purchases.state.PurchaseHistoryState.load_purchases)

# --- Páginas Privadas de Administración ---
app.add_page(blog.list.blog_post_list_page, route=navigation.routes.BLOG_POSTS_ROUTE, on_load=blog.state.BlogPostState.load_posts)
app.add_page(blog.detail.blog_post_detail_page, route=f"{navigation.routes.BLOG_POSTS_ROUTE}/[blog_id]", on_load=blog.state.BlogPostState.get_post_detail)
app.add_page(blog.add.blog_post_add_page, route=navigation.routes.BLOG_POST_ADD_ROUTE)
app.add_page(blog.edit.blog_post_edit_page, route="/blog/[blog_id]/edit", on_load=blog.state.BlogEditFormState.on_load_edit)
app.add_page(admin.page.admin_confirm_page, route="/admin/confirm-payments", title="Confirmar Pagos", on_load=admin.state.AdminConfirmState.load_pending_purchases)
app.add_page(admin.page.payment_history_page, route="/admin/payment-history", title="Historial de Pagos", on_load=admin.state.PaymentHistoryState.load_confirmed_purchases)

# Páginas de Contacto
app.add_page(contact.page.contact_page, route=navigation.routes.CONTACT_US_ROUTE)
app.add_page(contact.page.contact_entries_list_page, route=navigation.routes.CONTACT_ENTRIES_ROUTE, on_load=contact.state.ContactState.load_entries)