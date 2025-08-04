# likemodas/__init__.py (CORREGIDO Y COMPLETO)

import reflex as rx
import reflex_local_auth

from rxconfig import config

# --- Módulos específicos de la aplicación ---
from .auth import pages as auth_pages, state as auth_state, verify_state, reset_password_state
from .pages import (
    search_results, 
    about as about_page, 
    pricing as pricing_page, 
    dashboard as dashboard_component, 
    landing as landing_component, 
    test_page, 
    category_page
)
from .blog import (
    blog_public_page_content,
    blog_public_detail_content,
    blog_post_list_content,
    blog_post_detail_content,
    blog_post_add_content,
    blog_post_edit_content,
    state as blog_state
)
from .cart import page as cart_page, state as cart_state
from .purchases import page as purchases_page, state as purchases_state
from .admin import state as admin_state, page as admin_page
from .contact import page as contact_page, state as contact_state
from . import navigation
from .account import page as account_page_module, shipping_info as shipping_info_module, shipping_info_state
from .ui.base import base_page

class HomePageState(cart_state.CartState):
    @rx.event
    def on_load_main(self):
        self.current_category = ""
        yield cart_state.CartState.load_posts_and_set_category

def index_content() -> rx.Component:
    return blog_public_page_content()

# --- Configuración de la App ---
app = rx.App(
    theme=rx.theme(
        appearance="dark", 
        has_background=True, 
        panel_background="solid",
        radius="medium", 
        accent_color="sky"
    ),
)

# --- Definición de Rutas de la Aplicación ---

# ✅ LÍNEA CORREGIDA: Se añade 'route="/"' para la página de inicio.
app.add_page(base_page(index_content()), route="/", on_load=HomePageState.on_load_main)

app.add_page(base_page(dashboard_component.dashboard_content()), route="/dashboard", title="Dashboard", on_load=cart_state.CartState.on_load)
app.add_page(base_page(category_page.category_content()), route="/category/[cat_name]", title="Categoría", on_load=cart_state.CartState.load_posts_and_set_category)
app.add_page(base_page(search_results.search_results_content()), route="/search-results", title="Resultados de Búsqueda")

# --- Rutas de Autenticación ---
app.add_page(base_page(auth_pages.my_login_page_content()), route=reflex_local_auth.routes.LOGIN_ROUTE)
app.add_page(base_page(auth_pages.my_register_page_content()), route=reflex_local_auth.routes.REGISTER_ROUTE)
app.add_page(base_page(auth_pages.verification_page_content()), route="/verify-email", on_load=verify_state.VerifyState.verify_token)
app.add_page(base_page(auth_pages.forgot_password_page_content()), route="/forgot-password")
app.add_page(base_page(auth_pages.reset_password_page_content()), route="/reset-password", on_load=reset_password_state.ResetPasswordState.on_load_check_token)
app.add_page(base_page(auth_pages.my_logout_page_content()), route=navigation.routes.LOGOUT_ROUTE)

# --- Rutas de Páginas Estáticas y Navegación ---
app.add_page(base_page(about_page.about_page_content()), route=navigation.routes.ABOUT_US_ROUTE)
app.add_page(base_page(pricing_page.pricing_page_content()), route=navigation.routes.PRICING_ROUTE)
app.add_page(base_page(contact_page.contact_page_content()), route=navigation.routes.CONTACT_US_ROUTE)

# --- Rutas del Blog/Galería de Productos ---
app.add_page(base_page(blog_public_page_content()), route=navigation.routes.BLOG_PUBLIC_PAGE_ROUTE, title="Galería de Productos", on_load=cart_state.CartState.on_load)
app.add_page(
    base_page(blog_public_detail_content()), 
    route=f"{navigation.routes.BLOG_PUBLIC_DETAIL_ROUTE}/[id]",
    title="Detalle del Producto", 
    on_load=blog_state.CommentState.on_load
)
app.add_page(base_page(blog_post_list_content()), route=navigation.routes.BLOG_POSTS_ROUTE, on_load=blog_state.BlogPostState.load_posts)
app.add_page(base_page(blog_post_detail_content()), route=f"{navigation.routes.BLOG_POSTS_ROUTE}/[blog_id]", on_load=blog_state.BlogPostState.get_post_detail)
app.add_page(base_page(blog_post_add_content()), route=navigation.routes.BLOG_POST_ADD_ROUTE)
app.add_page(base_page(blog_post_edit_content()), route="/blog/[blog_id]/edit", on_load=blog_state.BlogEditFormState.on_load_edit)

# --- Rutas de Cuenta, Carrito y Compras ---
app.add_page(
    base_page(cart_page.cart_page_content()), 
    route="/cart", 
    title="Mi Carrito", 
    on_load=[cart_state.CartState.on_load, cart_state.CartState.load_default_shipping_info]
)
app.add_page(base_page(purchases_page.purchase_history_content()), route="/my-purchases", title="Mis Compras", on_load=purchases_state.PurchaseHistoryState.load_purchases)
app.add_page(base_page(account_page_module.my_account_redirect_content()), route=navigation.routes.MY_ACCOUNT_ROUTE, on_load=rx.redirect(navigation.routes.SHIPPING_INFO_ROUTE))
app.add_page(base_page(shipping_info_module.shipping_info_content()), route=navigation.routes.SHIPPING_INFO_ROUTE, title="Información de Envío", on_load=shipping_info_state.ShippingInfoState.load_addresses)

# --- Rutas de Administración ---
app.add_page(base_page(admin_page.admin_confirm_content()), route="/admin/confirm-payments", title="Confirmar Pagos", on_load=admin_state.AdminConfirmState.load_pending_purchases)
app.add_page(base_page(admin_page.payment_history_content()), route="/admin/payment-history", title="Historial de Pagos", on_load=admin_state.PaymentHistoryState.load_confirmed_purchases)
app.add_page(base_page(contact_page.contact_entries_list_content()), route=navigation.routes.CONTACT_ENTRIES_ROUTE, on_load=contact_state.ContactState.load_entries)