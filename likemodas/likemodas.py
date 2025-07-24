# likemodas/likemodas.py

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
        
        # --- Páginas Públicas Principales ---
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

        # --- Páginas de Usuario Autenticado (no admin) ---
        if route == "/dashboard":
            return dashboard_component.dashboard_component()
        if route == "/cart":
            return cart_page.cart_page()
        if route == "/my-purchases":
            return purchases_page.purchase_history_page()
        if route == "/my-account/shipping-info":
            return shipping_info_module.shipping_info_page()

        # --- Páginas de Admin ---
        if route == "/blog":
            return blog_list.blog_post_list_page()
        if route.startswith("/blog/") and route.endswith("/edit"):
            return blog_edit.blog_post_edit_page()
        if route.startswith("/blog/"):
            return blog_detail.blog_post_detail_page()
        if route == "/blog/add":
            return blog_add.blog_post_add_page()
        if route == "/admin/confirm-payments":
            return cart_page.admin_confirm_page() # Asumiendo que esta es la página correcta
        if route == "/admin/payment-history":
            return cart_page.payment_history_page() # Asumiendo que esta es la página correcta
        if route == "/contact/entries":
            return contact_page.contact_entries_list_page()

        # Si no coincide, devuelve un fragmento vacío para que se muestre la página 404
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
# 1. Rutas que serán manejadas por el componente raíz 'index'.
# Se listan explícitamente para que Reflex las reconozca.
PUBLIC_ROUTES = [
    "/",
    "/blog/page",
    "/blog-public/[blog_public_id]",
    "/category/[cat_name]",
    "/about",
    "/pricing",
    "/contact",
]
for route in PUBLIC_ROUTES:
    app.add_page(index, route=route)

# 2. Rutas que NO son públicas o tienen una lógica muy específica que no pasa por el 'index' público.
# (Principalmente autenticación y redirecciones especiales).
app.add_page(search_results.search_results_page, route="/search-results")
app.add_page(auth_pages.my_login_page, route=reflex_local_auth.routes.LOGIN_ROUTE)
app.add_page(auth_pages.my_register_page, route=reflex_local_auth.routes.REGISTER_ROUTE)
app.add_page(auth_pages.verification_page, route="/verify-email", on_load=verify_state.VerifyState.verify_token)
app.add_page(auth_pages.forgot_password_page, route="/forgot-password")
app.add_page(auth_pages.reset_password_page, route="/reset-password", on_load=reset_password_state.ResetPasswordState.on_load_check_token)
app.add_page(auth_pages.my_logout_page, route=navigation.routes.LOGOUT_ROUTE)
app.add_page(
    account_page_module.my_account_redirect_page, 
    route=navigation.routes.MY_ACCOUNT_ROUTE,
    on_load=rx.redirect(navigation.routes.SHIPPING_INFO_ROUTE)
)

# 3. Se asignan los eventos on_load a las rutas dinámicas manejadas por 'index'.
app.add_page_loader(cart_state.CartState.on_load, ["/", "/blog/page"])
app.add_page_loader(blog_public_detail.CommentState.on_load, "/blog-public/[blog_public_id]")
app.add_page_loader(category_page.CategoryPageState.load_category_posts, "/category/[cat_name]")