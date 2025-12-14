# likemodas/likemodas.py

from fastapi import FastAPI
import reflex as rx
import reflex_local_auth

# Módulos internos de la aplicación
from .api import webhooks, tasks as api_tasks
from .api import mobile_api
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

# Importamos la función 'display_settings_page' directamente
from .account.display_settings_page import display_settings_page

# Vistas de ADMINISTRADOR
from .admin import page as admin_page
from .admin import finance_page
from .admin.profile_page import admin_profile_page_content
from .admin.my_location_page import my_location_page_content
from .admin.store_page import admin_store_page
from .admin.tickets_page import admin_tickets_page_content
from .admin.users_page import user_management_page
from .admin import employees_page
from .admin.reports_page import reports_page_content

# Vistas de Blog y Productos
from .blog import blog_admin_page, blog_post_add_content
from .pages import landing, seller_page

# Vistas del proceso de compra
from .cart import page as cart_page
from .purchases import page as purchases_page
from .pages import payment_status, payment_pending, processing_payment
from likemodas.pages.delete_account_info import delete_account_info

# Importamos las páginas legales
from .pages.legal.terms_page import terms_page
from .pages.legal.privacy_page import privacy_page
from .pages.legal.cookies_page import cookies_page

# Vistas de soporte y facturas
from .invoice import page as invoice_page
from .invoice.state import InvoiceState
from .returns import page as returns_page



# Configuración del backend de FastAPI
fastapi_app = FastAPI(title="API extendida de Likemodas")
fastapi_app.include_router(webhooks.router)
fastapi_app.include_router(api_tasks.router)
fastapi_app.include_router(mobile_api.router)

# Configuración de la aplicación Reflex
app = rx.App(
    head_components=[
        rx.el.meta(name="description", content="Compra lo mejor en moda, calzado y accesorios en Likemodas. Envíos a toda Colombia. Calidad y estilo al mejor precio."),
        rx.el.meta(name="keywords", content="likemodas, ropa, calzado, colombia, moda, tienda online, zapatillas, bolsos"),
        rx.el.meta(property="og:title", content="Likemodas - Estilo y Calidad"),
        rx.el.meta(property="og:description", content="Descubre nuestra colección exclusiva."),
        rx.el.meta(property="og:image", content="/logo.png"),
    ],
    style={
        "font_family": "Arial, sans-serif",
        ".ToastViewport": {
            "z_index": "99999 !important",
        },
    },
    api_transformer=fastapi_app
)

# --- PÁGINA TRAMPOLÍN (SOLUCIÓN AL CONGELAMIENTO) ---
# Esta página carga instantáneamente, ejecuta la lógica y redirige.
# Evita cargar toda la Landing Page dentro de la ruta dinámica.
# Modificamos el handler para aceptar el ID como argumento (propiedad de Reflex)
def deep_link_handler():
    # Obtenemos el ID de la URL actual
    current_id = AppState.router.page.params.get("deep_id", "")
    
    # Construimos el link "fuerte": likemodas://product/123
    app_scheme_url = "likemodas://product/" + current_id

    return rx.box(
        # 1. Intentar abrir la App inmediatamente usando Javascript
        rx.script(f"window.location.href = '{app_scheme_url}';"),
        
        # 2. Mostrar spinner mientras carga la web (por si no tiene la app)
        rx.center(
            rx.spinner(color="violet", size="3"),
            rx.text("Abriendo...", margin_top="1em", color="gray"),
            height="100vh",
            width="100%",
            bg="white"
        ),
        # Ejecutar también la lógica original (cargar modal) para que la web funcione si falla la app
        on_mount=AppState.check_deep_link 
    )

# --- EN EL REGISTRO DE RUTAS ---
app.add_page(
    deep_link_handler(), 
    # Mantenemos la ruta web estándar
    route="/product/[deep_id]", 
)

# Usa la variable 'fastapi_app' que definiste más arriba en el archivo
@fastapi_app.get("/.well-known/assetlinks.json") 
async def assetlinks_endpoint():
    return [
      {
        "relation": ["delegate_permission/common.handle_all_urls"],
        "target": {
          "namespace": "android_app",
          "package_name": "com.likemodas.app",
          "sha256_cert_fingerprints": [
            "E9:BC:A9:3D:0D:95:42:00:1D:C1:EC:F1:11:1A:6E:EF:70:19:61:6F:9B:D5:DF:97:0F:89:5B:6A:CA:6B:38:F8"
          ]
        }
      }
    ]

# --- REGISTRO DE RUTAS ---

# Rutas Públicas y de Autenticación
app.add_page(base_page(landing.landing_content()), route="/", on_load=AppState.load_main_page_data, title="Likemodas - Inicio")

# --- RUTA DEEP LINK (SOLUCIÓN DEFINITIVA) ---
# 1. Usamos 'deep_link_handler' para evitar el crash/congelamiento.
# 2. Usamos '[deep_id]' para evitar el error de Shadowing con state.py.
app.add_page(
    deep_link_handler(), 
    route="/product/[deep_id]", 
    on_load=AppState.check_deep_link 
)

app.add_page(base_page(auth_pages.my_login_page_content()), route=reflex_local_auth.routes.LOGIN_ROUTE, title="Iniciar Sesión")
app.add_page(base_page(auth_pages.my_register_page_content()), route=reflex_local_auth.routes.REGISTER_ROUTE, title="Registrarse")
app.add_page(base_page(auth_pages.verification_page_content()), route="/verify-email", on_load=AppState.verify_token, title="Verificar Email")
app.add_page(base_page(auth_pages.forgot_password_page_content()), route="/forgot-password", title="Recuperar Contraseña")
app.add_page(base_page(auth_pages.reset_password_page_content()), route="/reset-password", on_load=AppState.on_load_check_token, title="Restablecer Contraseña")
app.add_page(base_page(tfa_verify_page_content()), route="/verify-2fa", title="Verificación 2FA")
app.add_page(base_page(seller_page.seller_page_content()), route="/vendedor", on_load=AppState.on_load_seller_page, title="Publicaciones del Vendedor")

# Rutas de la Cuenta de CLIENTE
app.add_page(user_profile_page.profile_page_content(), route="/my-account/profile", title="Mi Perfil", on_load=AppState.on_load_profile_page)
app.add_page(shipping_info_module.shipping_info_content(), route=navigation.routes.SHIPPING_INFO_ROUTE, title="Información de Envío", on_load=AppState.load_addresses)
app.add_page(saved_posts_module.saved_posts_content(), route="/my-account/saved-posts", title="Publicaciones Guardadas", on_load=AppState.on_load_saved_posts_page)
app.add_page(display_settings_page(), route="/my-account/display-settings", title="Configuración de Visualización")

# Rutas del Proceso de Compra
app.add_page(base_page(cart_page.cart_page_content()), route="/cart", title="Mi Carrito", on_load=[AppState.on_load, AppState.load_default_shipping_info])
app.add_page(purchases_page.purchase_history_content(), route="/my-purchases", title="Mis Compras", on_load=AppState.on_load_purchases_page)
app.add_page(base_page(payment_status.payment_status_page()), route="/payment-status", title="Estado del Pago")
app.add_page(base_page(payment_pending.payment_pending_page()), route="/payment-pending", title="Pago Pendiente")
app.add_page(processing_payment.processing_payment_page(), route="/processing-payment", on_load=AppState.start_sistecredito_polling, title="Procesando Pago")

# Rutas de Soporte y Facturas
app.add_page(invoice_page.invoice_page_content(), route="/invoice", on_load=AppState.on_load_invoice_page, title="Factura")
app.add_page(base_page(returns_page.return_exchange_page_content()), route=navigation.routes.RETURN_EXCHANGE_ROUTE, on_load=AppState.on_load_return_page, title="Devolución o Cambio")

# Rutas del Panel de ADMINISTRADOR
app.add_page(admin_profile_page_content(), route="/admin/profile", title="Perfil de Administrador", on_load=AppState.on_load_profile_page)
app.add_page(my_location_page_content(), route="/admin/my-location", on_load=AppState.on_load_seller_profile, title="Mi Ubicación de Origen")
app.add_page(
    base_page(blog_admin_page()), 
    route="/blog", 
    title="Mis Publicaciones",
    on_load=[
        AppState.sync_user_context,
        AppState.load_mis_publicaciones
    ]
)
app.add_page(base_page(finance_page.finance_page_content()), route="/admin/finance", on_load=AppState.on_load_finance_data, title="Finanzas")
app.add_page(base_page(user_management_page()), route="/admin/users", on_load=AppState.load_all_users, title="Gestión de Usuarios")
app.add_page(base_page(blog_post_add_content()), route=navigation.routes.BLOG_POST_ADD_ROUTE, title="Añadir Producto")
app.add_page(base_page(admin_page.admin_confirm_content()), route="/admin/confirm-payments", title="Gestionar Órdenes", on_load=AppState.load_active_purchases)
app.add_page(base_page(admin_store_page()), route="/admin/store", on_load=[AppState.on_load_admin_store, AppState.process_qr_url_on_load], title="Admin | Tienda")
app.add_page(base_page(admin_page.payment_history_content()), route="/admin/payment-history", title="Historial de Pagos", on_load=AppState.load_purchase_history)
app.add_page(base_page(admin_tickets_page_content()), route=navigation.routes.SUPPORT_TICKETS_ROUTE, on_load=AppState.on_load_admin_tickets_page, title="Solicitudes de Soporte")
app.add_page(base_page(employees_page.employees_management_page()), route="/admin/employees", on_load=AppState.load_empleados, title="Gestión de Empleados")
app.add_page(base_page(reports_page_content()), route="/admin/reports", on_load=AppState.load_admin_reports, title="Gestión de Reportes")

# Páginas Legales
app.add_page(terms_page, route="/terms", title="Términos y Condiciones")
app.add_page(privacy_page, route="/privacy", title="Política de Privacidad")
app.add_page(cookies_page, route="/cookies", title="Política de Cookies")

# Eliminar cuenta
app.add_page(delete_account_info, route="/delete-account-info", title="Eliminar Cuenta")