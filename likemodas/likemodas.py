# likemodas/likemodas.py

from fastapi import FastAPI
import reflex as rx
import reflex_local_auth

# Módulos internos de la aplicación
from .api import webhooks, tasks as api_tasks
from .state import AppState
from .ui.base import base_page
from . import navigation

# Vistas de autenticación
from .auth import pages as auth_pages
from .auth.tfa_verify_page import tfa_verify_page_content

# Vistas de la cuenta de CLIENTE
from .account import profile_page as user_profile_page
from .account import shipping_info as shipping_info_module
from .account import saved_posts as saved_posts_module

# Vistas de ADMINISTRADOR
from .admin import page as admin_page
from .admin import finance_page
from .admin.profile_page import admin_profile_page_content
from .admin.my_location_page import my_location_page_content
from .admin.store_page import admin_store_page
from .admin.tickets_page import admin_tickets_page_content
from .admin.users_page import user_management_page
from .admin import employees_page # Importa la nueva página

# Vistas de Blog y Productos
from .blog import blog_admin_page, blog_post_add_content
from .pages import landing, seller_page

# Vistas del proceso de compra
from .cart import page as cart_page
from .purchases import page as purchases_page
from .pages import payment_status, payment_pending, processing_payment

# Vistas de soporte y facturas
from .invoice import page as invoice_page
from .invoice.state import InvoiceState
from .returns import page as returns_page

# Configuración del backend de FastAPI
fastapi_app = FastAPI(title="API extendida de Likemodas")
fastapi_app.include_router(webhooks.router)
fastapi_app.include_router(api_tasks.router)

# Configuración de la aplicación Reflex
app = rx.App(
    style={"font_family": "Arial, sans-serif"},
    api_transformer=fastapi_app
)

# --- REGISTRO DE RUTAS ---

# Rutas Públicas y de Autenticación
app.add_page(base_page(landing.landing_content()), route="/", on_load=AppState.load_main_page_data, title="Likemodas | Inicio")
app.add_page(base_page(auth_pages.my_login_page_content()), route=reflex_local_auth.routes.LOGIN_ROUTE, title="Iniciar Sesión")
app.add_page(base_page(auth_pages.my_register_page_content()), route=reflex_local_auth.routes.REGISTER_ROUTE, title="Registrarse")
app.add_page(base_page(auth_pages.verification_page_content()), route="/verify-email", on_load=AppState.verify_token, title="Verificar Email")
app.add_page(base_page(auth_pages.forgot_password_page_content()), route="/forgot-password", title="Recuperar Contraseña")
app.add_page(base_page(auth_pages.reset_password_page_content()), route="/reset-password", on_load=AppState.on_load_check_token, title="Restablecer Contraseña")
app.add_page(base_page(tfa_verify_page_content()), route="/verify-2fa", title="Verificación 2FA")
app.add_page(base_page(seller_page.seller_page_content()), route="/vendedor", on_load=AppState.on_load_seller_page, title="Publicaciones del Vendedor")

# Rutas de la Cuenta de CLIENTE
# Esta línea ya era correcta y sirve de modelo.
app.add_page(user_profile_page.profile_page_content(), route="/my-account/profile", title="Mi Perfil", on_load=AppState.on_load_profile_page)

# --- INICIO DE LA CORRECCIÓN ---
# Se elimina la envoltura "base_page(...)" de las siguientes líneas.
# La función de la página ya se encarga de llamar al layout correcto.
app.add_page(shipping_info_module.shipping_info_content(), route=navigation.routes.SHIPPING_INFO_ROUTE, title="Información de Envío", on_load=AppState.load_addresses)
app.add_page(saved_posts_module.saved_posts_content(), route="/my-account/saved-posts", title="Publicaciones Guardadas", on_load=AppState.on_load_saved_posts_page)
# --- FIN DE LA CORRECCIÓN ---


# Rutas del Proceso de Compra
app.add_page(base_page(cart_page.cart_page_content()), route="/cart", title="Mi Carrito", on_load=[AppState.on_load, AppState.load_default_shipping_info])

# --- INICIO DE LA CORRECCIÓN ---
app.add_page(purchases_page.purchase_history_content(), route="/my-purchases", title="Mis Compras", on_load=AppState.on_load_purchases_page)
# --- FIN DE LA CORRECCIÓN ---

app.add_page(base_page(payment_status.payment_status_page()), route="/payment-status", title="Estado del Pago")
app.add_page(base_page(payment_pending.payment_pending_page()), route="/payment-pending", title="Pago Pendiente")
app.add_page(processing_payment.processing_payment_page(), route="/processing-payment", on_load=AppState.start_sistecredito_polling, title="Procesando Pago")

# Rutas de Soporte y Facturas
# Nota: La página de facturas no usa base_page porque es para imprimir. Esto es correcto.
app.add_page(invoice_page.invoice_page_content(), route="/invoice", on_load=InvoiceState.on_load_invoice_page, title="Factura")
app.add_page(base_page(returns_page.return_exchange_page_content()), route=navigation.routes.RETURN_EXCHANGE_ROUTE, on_load=AppState.on_load_return_page, title="Devolución o Cambio")

# Rutas del Panel de ADMINISTRADOR
# Nota: Estas páginas ya llaman a su propio layout, por lo que algunas usan base_page y otras no, lo cual es correcto.
app.add_page(admin_profile_page_content(), route="/admin/profile", title="Perfil de Administrador", on_load=AppState.on_load_profile_page)
app.add_page(my_location_page_content(), route="/admin/my-location", on_load=AppState.on_load_seller_profile, title="Mi Ubicación de Origen")
app.add_page(base_page(blog_admin_page()), route="/blog", title="Mis Publicaciones")
app.add_page(base_page(finance_page.finance_page_content()), route="/admin/finance", on_load=AppState.on_load_finance_data, title="Finanzas")
app.add_page(base_page(user_management_page()), route="/admin/users", on_load=AppState.load_all_users, title="Gestión de Usuarios")
app.add_page(base_page(blog_post_add_content()), route=navigation.routes.BLOG_POST_ADD_ROUTE, title="Añadir Producto")
app.add_page(base_page(admin_page.admin_confirm_content()), route="/admin/confirm-payments", title="Gestionar Órdenes", on_load=AppState.load_active_purchases)
app.add_page(base_page(admin_store_page()), route="/admin/store", on_load=[AppState.on_load_admin_store, AppState.process_qr_url_on_load], title="Admin | Tienda")
app.add_page(base_page(admin_page.payment_history_content()), route="/admin/payment-history", title="Historial de Pagos", on_load=AppState.load_purchase_history)
app.add_page(base_page(admin_tickets_page_content()), route=navigation.routes.SUPPORT_TICKETS_ROUTE, on_load=AppState.on_load_admin_tickets_page, title="Solicitudes de Soporte")
app.add_page(base_page(employees_page.employees_management_page()), route="/admin/employees", on_load=AppState.load_empleados, title="Gestión de Empleados")
