import reflex as rx
import reflex_local_auth

from rxconfig import config

# --- Módulos específicos ---
from .auth import pages as auth_pages
from .auth.state import SessionState
from .auth import verify_state
from .auth import reset_password_state
from .pages import search_results, about_page, pricing_page, dashboard_component, category_page
from .blog import (
    page as blog_page, 
    public_detail as blog_public_detail, 
    list as blog_list, 
    detail as blog_detail, 
    add as blog_add, 
    edit as blog_edit, 
    state as blog_state
)
from .cart import page as cart_page, state as cart_state
from .purchases import page as purchases_page, state as purchases_state
from .admin import state as admin_state
from .contact import page as contact_page, state as contact_state
from . import navigation
from .account import page as account_page_module, shipping_info as shipping_info_module, shipping_info_state

from .ui.base import base_page

# --- ESTADO RAÍZ PARA MANEJAR LA PÁGINA ACTUAL ---
class RootState(SessionState):
    @rx.var
    def current_page(self) -> rx.Component:
        route = self.router.page.path
        
        # --- Páginas Públicas ---
        if route == "/" or route == "/blog/page":
            return blog_page.blog_public_page()
        if route.startswith("/blog-public/"):
            return blog_public_detail.blog_public_detail_page()
        if route.startswith("/category/"):
            return category_page.category_page()
        if route == "/about":
            return about_page.about_page()
        if route == "/pricing":
            return pricing_page.pricing_page()
        if route == "/contact":
            return contact_page.contact_page()
            
        # --- Páginas de Usuario / Admin (se renderizan dentro de base_page) ---
        # No es necesario listarlas aquí, base_page las manejará.
        # Simplemente devolvemos un componente vacío y base_page mostrará el
        # contenido correcto basado en su propia lógica interna para rutas protegidas.
        return rx.fragment()

# --- FUNCIÓN DE PÁGINA PRINCIPAL (ÚNICA) ---
def index() -> rx.Component:
    return base_page(RootState.current_page)

# --- CONFIGURACIÓN DE LA APP ---
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

# --- REGISTRO DE PÁGINAS ---

# 1. Rutas públicas que usan la lógica del 'index' y necesitan on_load
app.add_page(index, route="/", on_load=cart_state.CartState.on_load)
app.add_page(index, route="/blog/page", on_load=cart_state.CartState.on_load)
app.add_page(index, route="/blog-public/[blog_public_id]", on_load=blog_public_detail.CommentState.on_load)
app.add_page(index, route="/category/[cat_name]", on_load=category_page.CategoryPageState.load_category_posts)

# 2. Rutas públicas que usan 'index' pero no necesitan on_load
app.add_page(index, route="/about")
app.add_page(index, route="/pricing")
app.add_page(index, route="/contact")

# 3. Páginas que NO usan la lógica del 'index' (autenticación, cuenta, admin, etc.)
app.add_page(search_results.search_results_page, route="/search-results")
app.add_page(auth_pages.my_login_page, route=reflex_local_auth.routes.LOGIN_ROUTE)
app.add_page(auth_pages.my_register_page, route=reflex_local_auth.routes.REGISTER_ROUTE)
app.add_page(auth_pages.verification_page, route="/verify-email", on_load=verify_state.VerifyState.verify_token)
app.add_page(auth_pages.forgot_password_page, route="/forgot-password")
app.add_page(auth_pages.reset_password_page, route="/reset-password", on_load=reset_password_state.ResetPasswordState.on_load_check_token)
app.add_page(auth_pages.my_logout_page, route=navigation.routes.LOGOUT_ROUTE)
app.add_page(
    cart_page.cart_page, 
    route="/cart", 
    on_load=[cart_state.CartState.on_load, cart_state.CartState.load_default_shipping_info]
)
app.add_page(purchases_page.purchase_history_page, route="/my-purchases", on_load=purchases_state.PurchaseHistoryState.load_purchases)
app.add_page(
    account_page_module.my_account_redirect_page, 
    route=navigation.routes.MY_ACCOUNT_ROUTE,
    on_load=rx.redirect(navigation.routes.SHIPPING_INFO_ROUTE)
)
app.add_page(
    shipping_info_module.shipping_info_page,
    route=navigation.routes.SHIPPING_INFO_ROUTE,
    on_load=shipping_info_state.ShippingInfoState.load_addresses 
)
app.add_page(blog_list.blog_post_list_page, route=navigation.routes.BLOG_POSTS_ROUTE, on_load=blog_state.BlogPostState.load_posts)
app.add_page(blog_detail.blog_post_detail_page, route=f"{navigation.routes.BLOG_POSTS_ROUTE}/[blog_id]", on_load=blog_state.BlogPostState.get_post_detail)
app.add_page(blog_add.blog_post_add_page, route=navigation.routes.BLOG_POST_ADD_ROUTE)
app.add_page(blog_edit.blog_post_edit_page, route="/blog/[blog_id]/edit", on_load=blog_state.BlogEditFormState.on_load_edit)
app.add_page(admin_page.admin_confirm_page, route="/admin/confirm-payments", on_load=admin_state.AdminConfirmState.load_pending_purchases)
app.add_page(admin_page.payment_history_page, route="/admin/payment-history", on_load=admin_state.PaymentHistoryState.load_confirmed_purchases)
app.add_page(contact_page.contact_entries_list_page, route=navigation.routes.CONTACT_ENTRIES_ROUTE, on_load=contact_state.ContactState.load_entries)