# likemodas/likemodas.py

import reflex as rx
import reflex_local_auth

from rxconfig import config

# --- Módulos específicos ---
from .auth import pages as auth_pages, state as auth_state, verify_state, reset_password_state
from .pages import search_results, about_page, pricing_page, dashboard_component, landing_component, test_page, category_page
from .blog import page as blog_page, public_detail as blog_public_detail, list as blog_list, detail as blog_detail, add as blog_add, edit as blog_edit, state as blog_state
from .cart import page as cart_page, state as cart_state
from .purchases import page as purchases_page, state as purchases_state
from .contact import page as contact_page, state as contact_state
from . import navigation
from .account import page as account_page_module, shipping_info as shipping_info_module, shipping_info_state

# --- ✅ SOLUCIÓN: Se importa state y page de admin desde el lugar correcto ---
from .admin import state as admin_state
from .admin import page as admin_page

from .ui.base import base_page

class HomePageState(cart_state.CartState):
    """Estado específico para la página de inicio."""
    @rx.event
    def on_load_main(self):
        self.current_category = ""
        yield cart_state.CartState.load_posts_and_set_category

def index() -> rx.Component:
    """La página principal ahora es la galería de productos."""
    return blog_page.blog_public_page()

app = rx.App(
    theme=rx.theme(
        appearance="dark", has_background=True, panel_background="solid",
        scaling="90%", radius="medium", accent_color="sky"
    ),
)

# --- Definición de Rutas de la Aplicación ---
app.add_page(index, on_load=HomePageState.on_load_main)
app.add_page(dashboard_component, route="/dashboard", title="Dashboard", on_load=cart_state.CartState.on_load)
app.add_page(category_page, route="/category/[cat_name]", title="Categoría", on_load=cart_state.CartState.load_posts_and_set_category)
app.add_page(search_results.search_results_page, route="/search-results", title="Resultados de Búsqueda")
app.add_page(auth_pages.my_login_page, route=reflex_local_auth.routes.LOGIN_ROUTE)
app.add_page(auth_pages.my_register_page, route=reflex_local_auth.routes.REGISTER_ROUTE)
app.add_page(auth_pages.verification_page, route="/verify-email", on_load=verify_state.VerifyState.verify_token)
app.add_page(auth_pages.forgot_password_page, route="/forgot-password")
app.add_page(auth_pages.reset_password_page, route="/reset-password", on_load=reset_password_state.ResetPasswordState.on_load_check_token)
app.add_page(auth_pages.my_logout_page, route=navigation.routes.LOGOUT_ROUTE)
app.add_page(about_page, route=navigation.routes.ABOUT_US_ROUTE)
app.add_page(pricing_page, route=navigation.routes.PRICING_ROUTE)
app.add_page(blog_page.blog_public_page, route=navigation.routes.BLOG_PUBLIC_PAGE_ROUTE, title="Galería de Productos", on_load=cart_state.CartState.on_load)
app.add_page(blog_public_detail.blog_public_detail_page, route=f"{navigation.routes.BLOG_PUBLIC_DETAIL_ROUTE}/[blog_public_id]", title="Detalle del Producto", on_load=blog_state.CommentState.on_load)
app.add_page(cart_page.cart_page, route="/cart", title="Mi Carrito", on_load=[cart_state.CartState.on_load, cart_state.CartState.load_default_shipping_info])
app.add_page(purchases_page.purchase_history_page, route="/my-purchases", title="Mis Compras", on_load=purchases_state.PurchaseHistoryState.load_purchases)
app.add_page(account_page_module.my_account_redirect_page, route=navigation.routes.MY_ACCOUNT_ROUTE, on_load=rx.redirect(navigation.routes.SHIPPING_INFO_ROUTE))
app.add_page(shipping_info_module.shipping_info_page, route=navigation.routes.SHIPPING_INFO_ROUTE, title="Información de Envío", on_load=shipping_info_state.ShippingInfoState.load_addresses)
app.add_page(blog_list.blog_post_list_page, route=navigation.routes.BLOG_POSTS_ROUTE, on_load=blog_state.BlogPostState.load_posts)
app.add_page(blog_detail.blog_post_detail_page, route=f"{navigation.routes.BLOG_POSTS_ROUTE}/[blog_id]", on_load=blog_state.BlogPostState.get_post_detail)
app.add_page(blog_add.blog_post_add_page, route=navigation.routes.BLOG_POST_ADD_ROUTE)
app.add_page(blog_edit.blog_post_edit_page, route="/blog/[blog_id]/edit", on_load=blog_state.BlogEditFormState.on_load_edit)
app.add_page(admin_page.admin_confirm_page, route="/admin/confirm-payments", title="Confirmar Pagos", on_load=admin_state.AdminConfirmState.load_pending_purchases)
app.add_page(admin_page.payment_history_page, route="/admin/payment-history", title="Historial de Pagos", on_load=admin_state.PaymentHistoryState.load_confirmed_purchases)
app.add_page(contact_page.contact_page, route=navigation.routes.CONTACT_US_ROUTE)
app.add_page(contact_page.contact_entries_list_page, route=navigation.routes.CONTACT_ENTRIES_ROUTE, on_load=contact_state.ContactState.load_entries)