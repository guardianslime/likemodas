# likemodas/likemodas.py (VERSIÓN FINAL)

import reflex as rx
import reflex_local_auth

from likemodas.account import profile_page
from likemodas.admin.profile_page import seller_profile_page
from likemodas.admin.tickets_page import admin_tickets_page_content

from .state import AppState, wompi_webhook
from .ui.base import base_page

from .auth import pages as auth_pages
from .invoice import page as invoice_page
from .invoice.state import InvoiceState # <-- AÑADE ESTA IMPORTACIÓN
# Asegúrate de que 'landing' esté importado desde .pages
from .pages import landing, search_results, category_page, seller_page # <-- Añade seller_page
from .returns import page as returns_page

from .blog import (
    blog_public_page_content, 
    blog_admin_page, 
    blog_post_add_content
)
from .cart import page as cart_page
from .purchases import page as purchases_page
from .admin import page as admin_page
from .admin.store_page import admin_store_page
from .admin.users_page import user_management_page
from .contact import page as contact_page
from .account import shipping_info as shipping_info_module
from .account import saved_posts as saved_posts_module # <-- AÑADE ESTA IMPORTACIÓN
from . import navigation

# --- ✨ INICIO DE LA CORRECCIÓN ✨ ---
# 1. Se elimina el argumento 'endpoints' de la inicialización de la app.
app = rx.App(
    style={"font_family": "Arial, sans-serif"},
)


# --- Ruta principal (la galería de productos) ---
app.add_page(
    base_page(landing.landing_content()),
    route="/",
    # --- CAMBIO CLAVE: Se usa el nuevo orquestador ---
    on_load=AppState.load_main_page_data,
    title="Likemodas | Inicio"
)

# AÑADE ESTA RUTA (puede ser después de las de búsqueda)
app.add_page(
    base_page(seller_page.seller_page_content()), 
    route="/vendedor",  # <-- Ruta fija, sin corchetes
    on_load=AppState.on_load_seller_page,
    title="Publicaciones del Vendedor"
)


# --- Rutas de Autenticación ---
app.add_page(base_page(auth_pages.my_login_page_content()), route=reflex_local_auth.routes.LOGIN_ROUTE, title="Iniciar Sesión")
app.add_page(base_page(auth_pages.my_register_page_content()), route=reflex_local_auth.routes.REGISTER_ROUTE, title="Registrarse")
app.add_page(base_page(auth_pages.verification_page_content()), route="/verify-email", on_load=AppState.verify_token, title="Verificar Email")
app.add_page(base_page(auth_pages.forgot_password_page_content()), route="/forgot-password", title="Recuperar Contraseña")
app.add_page(base_page(auth_pages.reset_password_page_content()), route="/reset-password", on_load=AppState.on_load_check_token, title="Restablecer Contraseña")

# --- Rutas de Búsqueda ---
app.add_page(base_page(search_results.search_results_content()), route="/search-results", title="Resultados de Búsqueda")

# ✨ AÑADE ESTA NUEVA RUTA ✨
app.add_page(
    base_page(profile_page.profile_page_content()), 
    route="/my-account/profile", 
    title="Mi Perfil", 
    on_load=AppState.on_load_profile_page
)

# --- Rutas de Cuenta, Carrito y Compras ---
app.add_page(base_page(cart_page.cart_page_content()), route="/cart", title="Mi Carrito", on_load=[AppState.on_load, AppState.load_default_shipping_info])
app.add_page(base_page(purchases_page.purchase_history_content()), route="/my-purchases", title="Mis Compras", on_load=AppState.load_purchases)
app.add_page(base_page(shipping_info_module.shipping_info_content()), route=navigation.routes.SHIPPING_INFO_ROUTE, title="Información de Envío", on_load=AppState.load_addresses)
app.add_page(base_page(saved_posts_module.saved_posts_content()), route="/my-account/saved-posts", title="Publicaciones Guardadas", on_load=AppState.on_load_saved_posts_page)

# --- Rutas de Administración ---
app.add_page(
    base_page(blog_admin_page()), 
    route="/blog", 
    title="Mis Publicaciones"
)
app.add_page(
    base_page(user_management_page()), 
    route="/admin/users", 
    on_load=AppState.load_all_users,
    title="Gestión de Usuarios"
)
app.add_page(
    base_page(blog_post_add_content()), 
    route=navigation.routes.BLOG_POST_ADD_ROUTE, 
    title="Añadir Producto"
)

# --- Añadir esta ruta dentro de la sección de Rutas de Administración ---
app.add_page(
    base_page(seller_profile_page()),
    route="/admin/my-location",
    on_load=AppState.on_load_seller_profile,
    title="Mi Ubicación de Origen"
)
app.add_page(
    base_page(admin_page.admin_confirm_content()),
    route="/admin/confirm-payments",
    title="Gestionar Órdenes", # Título opcional actualizado
    on_load=AppState.load_active_purchases # ✨ Asegúrate que llame a la función renombrada
)
app.add_page(
    base_page(admin_store_page()), 
    route="/admin/store", 
    on_load=AppState.on_load_admin_store,
    title="Admin | Tienda"
)
app.add_page(
    base_page(admin_page.payment_history_content()),
    route="/admin/payment-history",
    title="Historial de Pagos",
    on_load=AppState.load_purchase_history # ✨ Llama a la función con el nuevo nombre
)
app.add_page(
    base_page(admin_tickets_page_content()),
    route=navigation.routes.SUPPORT_TICKETS_ROUTE,
    on_load=AppState.on_load_admin_tickets_page,
    title="Solicitudes de Soporte"
)

app.add_page(
    invoice_page.invoice_page_content(),
    route="/invoice",
    on_load=InvoiceState.on_load_invoice_page, # <-- CAMBIA AppState POR InvoiceState
    title="Factura"
)

app.add_page(
    base_page(returns_page.return_exchange_page_content()),
    route=navigation.routes.RETURN_EXCHANGE_ROUTE,
    on_load=AppState.on_load_return_page,
    title="Devolución o Cambio",
)

# --- ✨ INICIO DE LA CORRECCIÓN ✨ ---
# Se elimina 'async' y 'await' porque la función llamada ya no es asíncrona.
@app.post("/api/wompi/webhook")
def wompi_webhook_endpoint(payload: dict):
    """
    Este es el endpoint que Wompi llamará. Solo acepta peticiones POST.
    """
    # Obtenemos el estado de forma síncrona, ya que estamos en un contexto de API
    state = rx.get_state(AppState)
    return wompi_webhook(payload, state)
# --- FIN DE LA CORRECCIÓN ✨ ---