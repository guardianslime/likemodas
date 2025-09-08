# likemodas/likemodas.py (Versión Final y Corregida)

import json
import reflex as rx
import reflex_local_auth

# Importaciones de las páginas de la aplicación
from likemodas.account import profile_page
from likemodas.admin.profile_page import seller_profile_page
from likemodas.admin.tickets_page import admin_tickets_page_content
from likemodas.ui.base import base_page
from likemodas.auth import pages as auth_pages
from likemodas.invoice import page as invoice_page
from likemodas.invoice.state import InvoiceState
from likemodas.pages import landing, search_results, seller_page
from likemodas.returns import page as returns_page
from likemodas.blog import (
    blog_admin_page, 
    blog_post_add_content
)
from likemodas.cart import page as cart_page
from likemodas.purchases import page as purchases_page
from likemodas.admin import page as admin_page
from likemodas.admin.store_page import admin_store_page
from likemodas.admin.users_page import user_management_page
from likemodas.contact import page as contact_page
from likemodas.account import shipping_info as shipping_info_module
from likemodas.account import saved_posts as saved_posts_module
from likemodas import navigation

# 1. Importamos la lógica del webhook y el estado principal.
from .state import AppState, wompi_webhook

# Inicialización de la aplicación Reflex
app = rx.App(
    style={"font_family": "Arial, sans-serif"},
)

# --- Ruta principal (la galería de productos) ---
app.add_page(
    base_page(landing.landing_content()),
    route="/",
    on_load=AppState.load_main_page_data,
    title="Likemodas | Inicio"
)
# --- Rutas de Vendedor y Búsqueda ---
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
# --- Rutas de Autenticación ---
app.add_page(base_page(auth_pages.my_login_page_content()), route=reflex_local_auth.routes.LOGIN_ROUTE, title="Iniciar Sesión")
app.add_page(base_page(auth_pages.my_register_page_content()), route=reflex_local_auth.routes.REGISTER_ROUTE, title="Registrarse")
app.add_page(base_page(auth_pages.verification_page_content()), route="/verify-email", on_load=AppState.verify_token, title="Verificar Email")
app.add_page(base_page(auth_pages.forgot_password_page_content()), route="/forgot-password", title="Recuperar Contraseña")
app.add_page(base_page(auth_pages.reset_password_page_content()), route="/reset-password", on_load=AppState.on_load_check_token, title="Restablecer Contraseña")
# --- Rutas de Cuenta, Carrito y Compras del Usuario ---
app.add_page(base_page(profile_page.profile_page_content()), route="/my-account/profile", title="Mi Perfil", on_load=AppState.on_load_profile_page)
app.add_page(base_page(cart_page.cart_page_content()), route="/cart", title="Mi Carrito", on_load=[AppState.on_load, AppState.load_default_shipping_info])
app.add_page(base_page(purchases_page.purchase_history_content()), route="/my-purchases", title="Mis Compras", on_load=AppState.load_purchases)
app.add_page(base_page(shipping_info_module.shipping_info_content()), route=navigation.routes.SHIPPING_INFO_ROUTE, title="Información de Envío", on_load=AppState.load_addresses)
app.add_page(base_page(saved_posts_module.saved_posts_content()), route="/my-account/saved-posts", title="Publicaciones Guardadas", on_load=AppState.on_load_saved_posts_page)
app.add_page(base_page(returns_page.return_exchange_page_content()), route=navigation.routes.RETURN_EXCHANGE_ROUTE, on_load=AppState.on_load_return_page, title="Devolución o Cambio")
# --- Rutas de Administración ---
app.add_page(base_page(blog_admin_page()), route="/blog", title="Mis Publicaciones")
app.add_page(base_page(user_management_page()), route="/admin/users", on_load=AppState.load_all_users, title="Gestión de Usuarios")
app.add_page(base_page(blog_post_add_content()), route=navigation.routes.BLOG_POST_ADD_ROUTE, title="Añadir Producto")
app.add_page(base_page(seller_profile_page()), route="/admin/my-location", on_load=AppState.on_load_seller_profile, title="Mi Ubicación de Origen")
app.add_page(base_page(admin_page.admin_confirm_content()), route="/admin/confirm-payments", title="Gestionar Órdenes", on_load=AppState.load_active_purchases)
app.add_page(base_page(admin_store_page()), route="/admin/store", on_load=AppState.on_load_admin_store, title="Admin | Tienda")
app.add_page(base_page(admin_page.payment_history_content()), route="/admin/payment-history", title="Historial de Pagos", on_load=AppState.load_purchase_history)
app.add_page(base_page(admin_tickets_page_content()), route=navigation.routes.SUPPORT_TICKETS_ROUTE, on_load=AppState.on_load_admin_tickets_page, title="Solicitudes de Soporte")
# --- Otras Rutas ---
app.add_page(invoice_page.invoice_page_content(), route="/invoice", on_load=InvoiceState.on_load_invoice_page, title="Factura")

# 2. Se define el endpoint de la API con la firma ASGI correcta.
#    Esta es la solución directa al error 'TypeError'.
@app._api("/wompi/webhook")
async def wompi_webhook_endpoint(scope, receive, send):
    """
    Este es el endpoint que Wompi llamará. Actúa como un "adaptador"
    entre el protocolo web crudo (ASGI) y la lógica de nuestra aplicación.
    """
    try:
        # Usamos rx.Request para manejar fácilmente la petición cruda.
        request = rx.Request(scope, receive, send)
        payload = await request.json()
        
        # Obtenemos una instancia del estado de la aplicación.
        state = await rx.get_state(AppState)
        
        # Llamamos a nuestra función de lógica de negocio, pasándole los datos.
        response_data = await wompi_webhook(payload, state)
        
        # Construimos una respuesta JSON estándar.
        response = rx.Response(
            content=json.dumps(response_data),
            media_type="application/json",
            status_code=200
        )
    except Exception as e:
        # Manejo de errores básico para depuración
        print(f"Error in webhook endpoint: {e}")
        response = rx.Response(
            content=json.dumps({"status": "error", "message": "Internal Server Error"}),
            media_type="application/json",
            status_code=500
        )
        
    # Enviamos la respuesta de vuelta al servidor (Wompi).
    await response(scope, receive, send)