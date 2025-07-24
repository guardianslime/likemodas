# likemodas/likemodas.py

import reflex as rx
import reflex_local_auth
from rxconfig import config

# --- Módulos específicos ---
from .auth import pages as auth_pages
from .auth.state import SessionState
from .auth import verify_state, reset_password_state
from .pages import search_results, about, pricing, dashboard, category_page
from .blog import page as blog_page, public_detail, list as blog_list, detail as blog_detail, add as blog_add, edit as blog_edit, state as blog_state
from .cart import page as cart_page, state as cart_state
from .purchases import page as purchases_page, state as purchases_state
from .admin import state as admin_state
from .contact import page as contact_page, state as contact_state
from . import navigation
from .account import page as account_page_module, shipping_info, shipping_info_state
from .ui.base import base_page

# --- Componente de Enrutamiento Principal ---
def frontend() -> rx.Component:
    return base_page(
        rx.match(
            rx.State.router.page.path,
            ("/", blog_page.blog_public_page()),
            ("/blog/page", blog_page.blog_public_page()),
            ("/about", about.about_page()),
            ("/pricing", pricing.pricing_page()),
            ("/contact", contact_page.contact_page()),
            ("/search-results", search_results.search_results_page()),
            ("/dashboard", dashboard.dashboard_component()),
            ("/cart", cart_page.cart_page()),
            ("/my-purchases", purchases_page.purchase_history_page()),
            ("/my-account/shipping-info", shipping_info.shipping_info_page()),
            ("/blog", blog_list.blog_post_list_page()),
            ("/blog/add", blog_add.blog_post_add_page()),
            ("/admin/confirm-payments", cart_page.admin_confirm_page()),
            ("/admin/payment-history", cart_page.payment_history_page()),
            ("/contact/entries", contact_page.contact_entries_list_page()),
            (blog_page.blog_public_page())
        )
    )

# --- CONFIGURACIÓN DE LA APP ---
app = rx.App()

# --- REGISTRO DE PÁGINAS ---
# Se elimina la ruta [[...splat]] y se registran las páginas individuales
app.add_page(frontend, route="/", on_load=cart_state.CartState.on_load)
app.add_page(frontend, route="/blog/page", on_load=cart_state.CartState.on_load)
app.add_page(frontend, route="/about")
app.add_page(frontend, route="/pricing")
app.add_page(frontend, route="/contact")
app.add_page(frontend, route="/search-results")
app.add_page(frontend, route="/dashboard", on_load=cart_state.CartState.on_load)
app.add_page(frontend, route="/cart", on_load=[cart_state.CartState.on_load, cart_state.CartState.load_default_shipping_info])
app.add_page(frontend, route="/my-purchases", on_load=purchases_page.PurchaseHistoryState.load_purchases)
app.add_page(frontend, route="/my-account/shipping-info", on_load=shipping_info_state.ShippingInfoState.load_addresses)
app.add_page(frontend, route="/blog", on_load=blog_state.BlogPostState.load_posts)
app.add_page(frontend, route="/blog/add", on_load=blog_state.BlogAddFormState)
app.add_page(frontend, route="/admin/confirm-payments", on_load=admin_state.AdminConfirmState.load_pending_purchases)
app.add_page(frontend, route="/admin/payment-history", on_load=admin_state.PaymentHistoryState.load_confirmed_purchases)
app.add_page(frontend, route="/contact/entries", on_load=contact_page.ContactState.load_entries)

# Páginas de autenticación y especiales que no usan el enrutador 'frontend'
app.add_page(auth_pages.my_login_page, route=reflex_local_auth.routes.LOGIN_ROUTE)
app.add_page(auth_pages.my_register_page, route=reflex_local_auth.routes.REGISTER_ROUTE)

# Páginas dinámicas que necesitan su propio 'on_load'
from .blog.state import CommentState
from .pages.category_page import CategoryPageState
app.add_page(frontend, route="/blog-public/[blog_public_id]", on_load=CommentState.on_load)
app.add_page(frontend, route="/category/[cat_name]", on_load=CategoryPageState.load_category_posts)

from .blog.state import BlogPostState, BlogEditFormState
app.add_page(frontend, route="/blog/[blog_id]", on_load=BlogPostState.get_post_detail)
app.add_page(frontend, route="/blog/[blog_id]/edit", on_load=BlogEditFormState.on_load_edit)