# likemodas/likemodas.py (VERSIÓN FINAL)

from fastapi import FastAPI
import reflex as rx
import reflex_local_auth

# Importaciones de Módulos y Páginas
from .api import webhooks
from .state import AppState
from .ui.base import base_page
from . import navigation

# Páginas de Autenticación
from .auth import pages as auth_pages

# Páginas de Cuenta de Usuario
from .account import profile_page
from .account import shipping_info as shipping_info_module
from .account import saved_posts as saved_posts_module

# Páginas de Administración
from .admin import page as admin_page
from .admin.profile_page import seller_profile_page
from .admin.store_page import admin_store_page
from .admin.tickets_page import admin_tickets_page_content
from .admin.users_page import user_management_page

# Páginas de la Tienda y Blog
from .blog import blog_admin_page, blog_post_add_content
from .pages import landing, search_results, seller_page

# Páginas de Proceso de Compra
from .cart import page as cart_page
from .purchases import page as purchases_page
from .pages import payment_status, payment_pending

# Otras páginas y módulos
from .invoice import page as invoice_page
from .invoice.state import InvoiceState
from .returns import page as returns_page

# 1. Crear la instancia de FastAPI que extenderá el backend de Reflex
fastapi_app = FastAPI(title="API extendida de Likemodas")

# 2. Incluir el router de webhooks
fastapi_app.include_router(webhooks.router)

# 3. Pasar la instancia de FastAPI a la aplicación Reflex
app = rx.App(
    style={"font_family": "Arial, sans-serif"},
    api_transformer=fastapi_app # <--- ¡LA CLAVE ESTÁ AQUÍ! [cite: 15]
)


# --- Ruta principal (la galería de productos) ---
app.add_page(
    base_page(landing.landing_content()),
    route="/",
    on_load=AppState.load_main_page_data,
    title="Likemodas | Inicio"
)

# --- Rutas de Autenticación ---
app.add_page(base_page(auth_pages.my_login_page_content()), route=reflex_local_auth.routes.LOGIN_ROUTE, title="Iniciar Sesión")
app.add_page(base_page(auth_pages.my_register_page_content()), route=reflex_local_auth.routes.REGISTER_ROUTE, title="Registrarse")
app.add_page(base_page(auth_pages.verification_page_content()), route="/verify-email", on_load=AppState.verify_token, title="Verificar Email")
app.add_page(base_page(auth_pages.forgot_password_page_content()), route="/forgot-password", title="Recuperar Contraseña")
app.add_page(base_page(auth_pages.reset_password_page_content()), route="/reset-password", on_load=AppState.on_load_check_token, title="Restablecer Contraseña")

# --- Rutas de Vistas Públicas ---
app.add_page(base_page(search_results.search_results_content()), route="/search-results", title="Resultados de Búsqueda")
app.add_page(base_page(seller_page.seller_page_content()), route="/vendedor", on_load=AppState.on_load_seller_page, title="Publicaciones del Vendedor")

# --- Rutas de Cuenta, Carrito y Compras ---
app.add_page(base_page(profile_page.profile_page_content()), route="/my-account/profile", title="Mi Perfil", on_load=AppState.on_load_profile_page)
app.add_page(base_page(cart_page.cart_page_content()), route="/cart", title="Mi Carrito", on_load=[AppState.on_load, AppState.load_default_shipping_info])
app.add_page(base_page(purchases_page.purchase_history_content()), route="/my-purchases", title="Mis Compras", on_load=AppState.load_purchases)
app.add_page(base_page(shipping_info_module.shipping_info_content()), route=navigation.routes.SHIPPING_INFO_ROUTE, title="Información de Envío", on_load=AppState.load_addresses)
app.add_page(base_page(saved_posts_module.saved_posts_content()), route="/my-account/saved-posts", title="Publicaciones Guardadas", on_load=AppState.on_load_saved_posts_page)

# --- Rutas de Administración ---
app.add_page(base_page(blog_admin_page()), route="/blog", title="Mis Publicaciones")
app.add_page(base_page(user_management_page()), route="/admin/users", on_load=AppState.load_all_users, title="Gestión de Usuarios")
app.add_page(base_page(blog_post_add_content()), route=navigation.routes.BLOG_POST_ADD_ROUTE, title="Añadir Producto")
app.add_page(base_page(seller_profile_page()), route="/admin/my-location", on_load=AppState.on_load_seller_profile, title="Mi Ubicación de Origen")
app.add_page(base_page(admin_page.admin_confirm_content()), route="/admin/confirm-payments", title="Gestionar Órdenes", on_load=AppState.load_active_purchases)
app.add_page(base_page(admin_store_page()), route="/admin/store", on_load=AppState.on_load_admin_store, title="Admin | Tienda")
app.add_page(base_page(admin_page.payment_history_content()), route="/admin/payment-history", title="Historial de Pagos", on_load=AppState.load_purchase_history)
app.add_page(base_page(admin_tickets_page_content()), route=navigation.routes.SUPPORT_TICKETS_ROUTE, on_load=AppState.on_load_admin_tickets_page, title="Solicitudes de Soporte")

# --- Rutas de Proceso de Compra y Post-Compra ---
app.add_page(invoice_page.invoice_page_content(), route="/invoice", on_load=InvoiceState.on_load_invoice_page, title="Factura")
app.add_page(base_page(returns_page.return_exchange_page_content()), route=navigation.routes.RETURN_EXCHANGE_ROUTE, on_load=AppState.on_load_return_page, title="Devolución o Cambio")
app.add_page(base_page(payment_status.payment_status_page()), route="/payment-status", title="Estado del Pago")
app.add_page(base_page(payment_pending.payment_pending_page()), route="/payment-pending", title="Pago Pendiente")