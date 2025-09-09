# likemodas/likemodas.py (Versión Final y Corregida)

# 1. Importamos 'app' desde el nuevo archivo central
from .app_def import app

# Importaciones del proyecto
import reflex_local_auth
from likemodas.ui.base import base_page
from likemodas.state import AppState
from likemodas.invoice.state import InvoiceState
from likemodas import navigation

# 2. Importamos el módulo de la API para que las rutas se registren al iniciar
from likemodas.api import wompi_api 

# Importaciones de todas las páginas
from likemodas.account import profile_page, saved_posts, shipping_info
from likemodas.admin import page as admin_page
from likemodas.admin.profile_page import seller_profile_page
from likemodas.admin.store_page import admin_store_page
from likemodas.admin.tickets_page import admin_tickets_page_content
from likemodas.admin.users_page import user_management_page
from likemodas.auth import pages as auth_pages
from likemodas.blog import blog_admin_page, blog_post_add_content
from likemodas.cart import page as cart_page
from likemodas.contact import page as contact_page
from likemodas.invoice import page as invoice_page
from likemodas.pages import landing, search_results, seller_page
from likemodas.purchases import page as purchases_page
from likemodas.returns import page as returns_page

# 3. La definición de 'app = rx.App(...)' se ELIMINÓ de este archivo.

# 2. Montamos la aplicación de FastAPI en la ruta /api
# Este es el método correcto y a prueba de versiones
app.mount(wompi_api, "/api")

# --- Añadimos todas las páginas al objeto 'app' importado ---
app.add_page(
    base_page(landing.landing_content()),
    route="/",
    on_load=AppState.load_main_page_data,
    title="Likemodas | Inicio"
)
app.add_page(
    base_page(seller_page.seller_page_content()), 
    route="/vendedor",
    on_load=AppState.on_load_seller_page,
    title="Publicaciones del Vendedor"
)
app.add_page(
    base_page(search_results.search_results_content()), 
    route="/search-results", 
    title="Resultados de Búsqueda"
)
app.add_page(base_page(auth_pages.my_login_page_content()), route=reflex_local_auth.routes.LOGIN_ROUTE, title="Iniciar Sesión")
app.add_page(base_page(auth_pages.my_register_page_content()), route=reflex_local_auth.routes.REGISTER_ROUTE, title="Registrarse")
app.add_page(base_page(auth_pages.verification_page_content()), route="/verify-email", on_load=AppState.verify_token, title="Verificar Email")
app.add_page(base_page(auth_pages.forgot_password_page_content()), route="/forgot-password", title="Recuperar Contraseña")
app.add_page(base_page(auth_pages.reset_password_page_content()), route="/reset-password", on_load=AppState.on_load_check_token, title="Restablecer Contraseña")
app.add_page(base_page(profile_page.profile_page_content()), route="/my-account/profile", title="Mi Perfil", on_load=AppState.on_load_profile_page)
app.add_page(base_page(cart_page.cart_page_content()), route="/cart", title="Mi Carrito", on_load=[AppState.on_load, AppState.load_default_shipping_info])
app.add_page(base_page(purchases_page.purchase_history_content()), route="/my-purchases", title="Mis Compras", on_load=AppState.load_purchases)
app.add_page(base_page(shipping_info.shipping_info_content()), route=navigation.routes.SHIPPING_INFO_ROUTE, title="Información de Envío", on_load=AppState.load_addresses)
app.add_page(base_page(saved_posts.saved_posts_content()), route="/my-account/saved-posts", title="Publicaciones Guardadas", on_load=AppState.on_load_saved_posts_page)
app.add_page(base_page(returns_page.return_exchange_page_content()), route=navigation.routes.RETURN_EXCHANGE_ROUTE, on_load=AppState.on_load_return_page, title="Devolución o Cambio")
app.add_page(base_page(blog_admin_page()), route="/blog", title="Mis Publicaciones")
app.add_page(base_page(user_management_page()), route="/admin/users", on_load=AppState.load_all_users, title="Gestión de Usuarios")
app.add_page(base_page(blog_post_add_content()), route=navigation.routes.BLOG_POST_ADD_ROUTE, title="Añadir Producto")
app.add_page(base_page(seller_profile_page()), route="/admin/my-location", on_load=AppState.on_load_seller_profile, title="Mi Ubicación de Origen")
app.add_page(base_page(admin_page.admin_confirm_content()), route="/admin/confirm-payments", title="Gestionar Órdenes", on_load=AppState.load_active_purchases)
app.add_page(base_page(admin_store_page()), route="/admin/store", on_load=AppState.on_load_admin_store, title="Admin | Tienda")
app.add_page(base_page(admin_page.payment_history_content()), route="/admin/payment-history", title="Historial de Pagos", on_load=AppState.load_purchase_history)
app.add_page(base_page(admin_tickets_page_content()), route=navigation.routes.SUPPORT_TICKETS_ROUTE, on_load=AppState.on_load_admin_tickets_page, title="Solicitudes de Soporte")
app.add_page(invoice_page.invoice_page_content(), route="/invoice", on_load=InvoiceState.on_load_invoice_page, title="Factura")