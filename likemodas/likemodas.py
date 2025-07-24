import reflex as rx
import reflex_local_auth

from rxconfig import config

# --- Módulos específicos ---
from .auth import pages as auth_pages
from .auth import state as auth_state
from .auth import verify_state
from .auth import reset_password_state
from .pages import search_results, about_page, pricing_page, dashboard_component, landing_component, test_page 
from .pages import category_page
from .blog import page as blog_page, public_detail as blog_public_detail, list as blog_list, detail as blog_detail, add as blog_add, edit as blog_edit, state as blog_state
from .cart import page as cart_page, state as cart_state
from .purchases import page as purchases_page, state as purchases_state
# --- CAMBIO: Se importa el nuevo módulo de admin ---
from .admin import state as admin_state
from .cart import page as admin_page # La página de admin sigue en cart/page.py por ahora
from .contact import page as contact_page, state as contact_state
from . import navigation
from .account import page as account_page_module
from .account import shipping_info as shipping_info_module
from .account import shipping_info_state

from .auth import pages as auth_pages
from .auth.state import SessionState
from .pages import category_page, search_results, about_page
from .blog import page as blog_page, public_detail as blog_public_detail
from .cart import page as cart_page, state as cart_state
from .ui.base import base_page  # Importamos base_page, que decide el layout

# --- NUEVO ESTADO PARA MANEJAR LA PÁGINA ACTUAL ---
class RootState(SessionState):
    @rx.var
    def current_page(self) -> rx.Component:
        """
        Renderiza el componente de la página correcta basándose en la ruta actual.
        """
        route = self.router.page.path
        
        if route == "/" or route == "/blog/page":
            return blog_page.blog_public_page()
        
        # Manejo de la página de detalle de producto
        if route.startswith("/blog-public/"):
            return blog_public_detail.blog_public_detail_page()
            
        # Manejo de las páginas de categoría
        if route.startswith("/category/"):
            return category_page.category_page()
        
        # Aquí puedes añadir otras rutas públicas si las tienes
        if route == "/about":
            return about_page.about_page()

        # Si no es ninguna de las anteriores, puede ser una página de admin,
        # de cuenta, etc., que ya son manejadas por base_page.
        # Devolvemos un fragmento vacío y dejamos que base_page maneje la lógica.
        return rx.fragment()

# --- NUEVA FUNCIÓN DE PÁGINA PRINCIPAL (ÚNICA) ---
def index() -> rx.Component:
    """
    La única página de entrada para la aplicación.
    Envuelve TODO en el tema y el layout base.
    """
    # Usamos base_page para que siga manejando la lógica de admin vs. público.
    # El contenido (child) será la página que decida el RootState.
    return base_page(RootState.current_page)

# --- CONFIGURACIÓN DE LA APP SIMPLIFICADA ---
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
# 1. Añadimos nuestra página raíz para que capture TODAS las rutas públicas.
app.add_page(index, route="/", on_load=cart_state.CartState.on_load)
app.add_page(index, route="/blog/page", on_load=cart_state.CartState.on_load)
app.add_page(index, route="/blog-public/[blog_public_id]", on_load=blog_public_detail.CommentState.on_load)
app.add_page(index, route="/category/[cat_name]", on_load=category_page.CategoryPageState.load_category_posts)
app.add_page(index, route="/about")


# 2. Añadimos las páginas que requieren una lógica específica o no son manejadas por la raíz
# (autenticación, carrito, cuenta, admin, etc.)
app.add_page(search_results.search_results_page, route="/search-results", title="Resultados de Búsqueda")
app.add_page(auth_pages.my_login_page, route=reflex_local_auth.routes.LOGIN_ROUTE)
app.add_page(auth_pages.my_register_page, route=reflex_local_auth.routes.REGISTER_ROUTE)
app.add_page(cart_page.cart_page, route="/cart", on_load=[cart_state.CartState.on_load, cart_state.CartState.load_default_shipping_info])


app.add_page(auth_pages.verification_page, route="/verify-email", on_load=verify_state.VerifyState.verify_token)
app.add_page(auth_pages.forgot_password_page, route="/forgot-password")
app.add_page(auth_pages.reset_password_page, route="/reset-password", on_load=reset_password_state.ResetPasswordState.on_load_check_token)
app.add_page(auth_pages.my_logout_page, route=navigation.routes.LOGOUT_ROUTE)
app.add_page(pricing_page, route=navigation.routes.PRICING_ROUTE)

# --- Páginas Públicas del Blog / Tienda ---
app.add_page(
    blog_page.blog_public_page,
    route=navigation.routes.BLOG_PUBLIC_PAGE_ROUTE,
    title="Galería de Productos",
    on_load=cart_state.CartState.on_load
)
app.add_page(
    blog_public_detail.blog_public_detail_page,
    route=f"{navigation.routes.BLOG_PUBLIC_DETAIL_ROUTE}/[blog_public_id]",
    title="Detalle del Producto",
    on_load=blog_state.CommentState.on_load
)

# --- Páginas de E-commerce del Usuario ---
app.add_page(
    cart_page.cart_page,
    route="/cart",
    title="Mi Carrito",
    # ✅ Esta configuración es correcta y crucial. Carga tanto los
    # productos como la dirección de envío predeterminada.
    on_load=[
        cart_state.CartState.on_load, 
        cart_state.CartState.load_default_shipping_info
    ]
)

app.add_page(purchases_page.purchase_history_page, route="/my-purchases", title="Mis Compras", on_load=purchases_state.PurchaseHistoryState.load_purchases)

# --- Nuevas Páginas de Cuenta de Usuario ---
app.add_page(
    account_page_module.my_account_redirect_page, 
    route=navigation.routes.MY_ACCOUNT_ROUTE,
    # 👇 AÑADE ESTA LÍNEA PARA MANEJAR LA REDIRECCIÓN
    on_load=rx.redirect(navigation.routes.SHIPPING_INFO_ROUTE)
)

app.add_page(
    shipping_info_module.shipping_info_page,
    route=navigation.routes.SHIPPING_INFO_ROUTE,
    title="Información de Envío",
    # 👇 Se carga la lista de direcciones al visitar la página
    on_load=shipping_info_state.ShippingInfoState.load_addresses 
)


# --- Páginas Privadas de Administración ---
app.add_page(blog_list.blog_post_list_page, route=navigation.routes.BLOG_POSTS_ROUTE, on_load=blog_state.BlogPostState.load_posts)
app.add_page(blog_detail.blog_post_detail_page, route=f"{navigation.routes.BLOG_POSTS_ROUTE}/[blog_id]", on_load=blog_state.BlogPostState.get_post_detail)
app.add_page(blog_add.blog_post_add_page, route=navigation.routes.BLOG_POST_ADD_ROUTE)
app.add_page(blog_edit.blog_post_edit_page, route="/blog/[blog_id]/edit", on_load=blog_state.BlogEditFormState.on_load_edit)
app.add_page(admin_page.admin_confirm_page, route="/admin/confirm-payments", title="Confirmar Pagos", on_load=admin_state.AdminConfirmState.load_pending_purchases)
app.add_page(admin_page.payment_history_page, route="/admin/payment-history", title="Historial de Pagos", on_load=admin_state.PaymentHistoryState.load_confirmed_purchases)

# Páginas de Contacto
app.add_page(contact_page.contact_page, route=navigation.routes.CONTACT_US_ROUTE)
app.add_page(contact_page.contact_entries_list_page, route=navigation.routes.CONTACT_ENTRIES_ROUTE, on_load=contact_state.ContactState.load_entries)